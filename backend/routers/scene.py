import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, delete, select

from database import get_session
from models.adaptation_strategy import AdaptationStrategy
from models.character import Character
from models.chapter import Chapter
from models.novel import Novel
from models.paragraph import Paragraph
from models.scene import Scene
from models.story_skeleton import StorySkeleton
from schemas.scene import SceneListResponse, SceneResponse
from services.llm_service import LLMService
from services.scene_planner_service import ScenePlannerService


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
    chapters = session.exec(select(Chapter).where(Chapter.novel_id == novel_id).order_by(Chapter.order_index)).all()
    paragraphs = session.exec(select(Paragraph).where(Paragraph.novel_id == novel_id).order_by(Paragraph.id)).all()
    characters = session.exec(select(Character).where(Character.novel_id == novel_id).order_by(Character.id)).all()
    strategy = session.exec(
        select(AdaptationStrategy)
        .where(AdaptationStrategy.novel_id == novel_id)
        .order_by(AdaptationStrategy.created_at.desc())
    ).first()
    skeleton = session.exec(
        select(StorySkeleton).where(StorySkeleton.novel_id == novel_id).order_by(StorySkeleton.created_at.desc())
    ).first()
    raw_scenes = ScenePlannerService(LLMService()).plan(
        novel,
        chapters,
        paragraphs,
        characters,
        system_prompt,
        scene_count,
        skeleton.content if skeleton else "",
        strategy.content if strategy else "",
    )

    if not raw_scenes:
        raise HTTPException(status_code=400, detail="小说段落不足，无法生成分场大纲")

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
