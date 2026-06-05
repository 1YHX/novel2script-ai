import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models.character import Character
from models.paragraph import Paragraph
from models.scene import Scene
from models.script import Script
from schemas.script import ScriptGenerateRequest, ScriptResponse, ScriptUpdateRequest
from services.llm_service import LLMError, LLMService


router = APIRouter(prefix="/api/scripts", tags=["scripts"])
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "script_generate.txt"


@router.post("/generate/{scene_id}", response_model=ScriptResponse)
def generate_script(
    scene_id: int,
    payload: ScriptGenerateRequest,
    session: Session = Depends(get_session),
) -> ScriptResponse:
    scene = session.get(Scene, scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="场景不存在")

    characters = session.exec(select(Character).where(Character.novel_id == scene.novel_id).order_by(Character.id)).all()
    source_paragraph_ids = _safe_json_loads(scene.source_paragraphs_json, [])
    paragraphs = []
    if source_paragraph_ids:
        limited_source_ids = source_paragraph_ids[:12]
        paragraphs = session.exec(
            select(Paragraph)
            .where(Paragraph.novel_id == scene.novel_id)
            .where((Paragraph.id.in_(limited_source_ids)) | (Paragraph.order_index.in_(limited_source_ids)))
            .order_by(Paragraph.id)
        ).all()
    if not paragraphs:
        paragraphs = session.exec(
            select(Paragraph).where(Paragraph.novel_id == scene.novel_id).order_by(Paragraph.id).limit(12)
        ).all()

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    user_prompt = "\n\n".join(
        [
            f"用户风格：{payload.style}",
            f"对白密度：{payload.dialogue_density}",
            f"是否包含镜头语言：{payload.include_camera_language}",
            "场景大纲：\n" + _format_scene(scene),
            "人物档案：\n" + _format_characters(characters),
            "对应原文段落：\n" + _format_paragraphs(paragraphs),
        ]
    )

    try:
        content = LLMService().chat(system_prompt, user_prompt)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    existing = session.exec(select(Script).where(Script.scene_id == scene_id).order_by(Script.version.desc())).first()
    version = existing.version + 1 if existing else 1
    script = Script(novel_id=scene.novel_id, scene_id=scene_id, content=content, version=version)
    session.add(script)
    session.commit()
    session.refresh(script)

    return _to_response(script)


@router.get("/{scene_id}", response_model=ScriptResponse)
def get_script(scene_id: int, session: Session = Depends(get_session)) -> ScriptResponse:
    script = session.exec(select(Script).where(Script.scene_id == scene_id).order_by(Script.version.desc())).first()
    if not script:
        raise HTTPException(status_code=404, detail="剧本不存在")
    return _to_response(script)


@router.put("/{script_id}", response_model=ScriptResponse)
def update_script(
    script_id: int,
    payload: ScriptUpdateRequest,
    session: Session = Depends(get_session),
) -> ScriptResponse:
    script = session.get(Script, script_id)
    if not script:
        raise HTTPException(status_code=404, detail="剧本不存在")

    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="剧本内容不能为空")

    new_script = Script(
        novel_id=script.novel_id,
        scene_id=script.scene_id,
        content=content,
        version=script.version + 1,
    )
    session.add(new_script)
    session.commit()
    session.refresh(new_script)
    return _to_response(new_script)


def _to_response(script: Script) -> ScriptResponse:
    return ScriptResponse(
        script_id=script.id,
        scene_id=script.scene_id,
        content=script.content,
        version=script.version,
    )


def _format_scene(scene: Scene) -> str:
    characters = "、".join(_safe_json_loads(scene.characters_json, []))
    paragraphs = "、".join(str(item) for item in _safe_json_loads(scene.source_paragraphs_json, []))
    return (
        f"场景编号：{scene.scene_index}\n"
        f"标题：{scene.title}\n"
        f"时间：{scene.time}\n"
        f"地点：{scene.location}\n"
        f"人物：{characters}\n"
        f"剧情目的：{scene.plot_goal}\n"
        f"冲突点：{scene.conflict}\n"
        f"对应段落：{paragraphs}"
    )


def _format_characters(characters: list[Character]) -> str:
    if not characters:
        return "暂无人物档案"
    lines = []
    for character in characters:
        personality = "、".join(_safe_json_loads(character.personality_json, []))
        relations = _safe_json_loads(character.relations_json, [])
        relation_text = "；".join(
            f"{item.get('target', '未知')} / {item.get('relation', '未知')}"
            for item in relations
            if isinstance(item, dict)
        )
        lines.append(
            f"- {character.name}：{character.role}；性格：{personality}；目标：{character.goal}；关系：{relation_text}"
        )
    return "\n".join(lines)


def _format_paragraphs(paragraphs: list[Paragraph]) -> str:
    if not paragraphs:
        return "未找到对应段落，请根据场景大纲生成。"
    return "\n".join(f"{paragraph.id}. {paragraph.content}" for paragraph in paragraphs)


def _safe_json_loads(value: str, default: list) -> list:
    try:
        loaded = json.loads(value)
        return loaded if isinstance(loaded, list) else default
    except json.JSONDecodeError:
        return default
