import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, delete, select

from database import get_session
from models.novel import Novel
from models.scene import Scene
from schemas.scene import SceneListResponse, SceneResponse
from services.llm_service import LLMError, LLMService


router = APIRouter(prefix="/api/scenes", tags=["scenes"])
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "scene_plan.txt"


@router.post("/plan/{novel_id}", response_model=SceneListResponse)
def plan_scenes(
    novel_id: int,
    scene_count: int = Query(default=5, ge=1, le=20),
    session: Session = Depends(get_session),
) -> SceneListResponse:
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    user_prompt = (
        f"小说标题：{novel.title}\n"
        f"目标场景数量：{scene_count}\n\n"
        f"小说正文：\n{novel.content[:16000]}"
    )

    try:
        result = LLMService().generate_json(system_prompt, user_prompt, "scenes")
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    raw_scenes = result.get("scenes")
    if not isinstance(raw_scenes, list):
        raise HTTPException(status_code=502, detail="分场大纲结果缺少 scenes 数组")

    session.exec(delete(Scene).where(Scene.novel_id == novel_id))
    session.commit()

    saved_scenes: list[Scene] = []
    for index, item in enumerate(raw_scenes, start=1):
        if not isinstance(item, dict):
            continue

        scene = Scene(
            novel_id=novel_id,
            scene_index=_safe_int(item.get("scene_id"), index),
            title=str(item.get("title", f"第 {index} 场")),
            time=str(item.get("time", "未知")),
            location=str(item.get("location", "未知")),
            characters_json=json.dumps(_ensure_string_list(item.get("characters")), ensure_ascii=False),
            plot_goal=str(item.get("plot_goal", "")),
            conflict=str(item.get("conflict", "")),
            source_paragraphs_json=json.dumps(_ensure_int_list(item.get("source_paragraphs")), ensure_ascii=False),
        )
        session.add(scene)
        saved_scenes.append(scene)

    session.commit()
    for scene in saved_scenes:
        session.refresh(scene)

    return SceneListResponse(scenes=[_to_response(scene) for scene in saved_scenes])


@router.get("/{novel_id}", response_model=SceneListResponse)
def get_scenes(novel_id: int, session: Session = Depends(get_session)) -> SceneListResponse:
    scenes = session.exec(select(Scene).where(Scene.novel_id == novel_id).order_by(Scene.scene_index)).all()
    return SceneListResponse(scenes=[_to_response(scene) for scene in scenes])


def _to_response(scene: Scene) -> SceneResponse:
    return SceneResponse(
        scene_id=scene.id,
        title=scene.title,
        time=scene.time,
        location=scene.location,
        characters=_safe_json_loads(scene.characters_json, []),
        plot_goal=scene.plot_goal,
        conflict=scene.conflict,
        source_paragraphs=_safe_json_loads(scene.source_paragraphs_json, []),
    )


def _ensure_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if value:
        return [str(value)]
    return []


def _ensure_int_list(value: Any) -> list[int]:
    if not isinstance(value, list):
        return []

    numbers: list[int] = []
    for item in value:
        try:
            numbers.append(int(item))
        except (TypeError, ValueError):
            continue
    return numbers


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_json_loads(value: str, default: Any) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default
