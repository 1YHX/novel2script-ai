import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models.character import Character
from models.check_report import CheckReport
from models.novel import Novel
from models.scene import Scene
from models.script import Script
from schemas.check import CheckIssueResponse, CheckReportResponse
from services.llm_service import LLMError, LLMService


router = APIRouter(prefix="/api/check", tags=["check"])
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "consistency_check.txt"


@router.post("/consistency/{novel_id}", response_model=CheckReportResponse)
def run_consistency_check(novel_id: int, session: Session = Depends(get_session)) -> CheckReportResponse:
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    characters = session.exec(select(Character).where(Character.novel_id == novel_id).order_by(Character.id)).all()
    scenes = session.exec(select(Scene).where(Scene.novel_id == novel_id).order_by(Scene.scene_index)).all()
    scripts = session.exec(select(Script).where(Script.novel_id == novel_id).order_by(Script.scene_id, Script.version)).all()

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    user_prompt = "\n\n".join(
        [
            f"小说标题：{novel.title}",
            "人物档案：\n" + _format_characters(characters),
            "分场大纲：\n" + _format_scenes(scenes),
            "已生成剧本：\n" + _format_scripts(scripts),
        ]
    )

    try:
        result = LLMService().generate_json(system_prompt, user_prompt, "consistency")
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    raw_issues = result.get("issues", [])
    if not isinstance(raw_issues, list):
        raise HTTPException(status_code=502, detail="一致性检查结果缺少 issues 数组")

    issues = [_normalize_issue(item) for item in raw_issues if isinstance(item, dict)]
    report = CheckReport(novel_id=novel_id, issues_json=json.dumps(issues, ensure_ascii=False))
    session.add(report)
    session.commit()

    return CheckReportResponse(issues=[CheckIssueResponse(**issue) for issue in issues])


@router.get("/reports/{novel_id}", response_model=CheckReportResponse)
def get_check_report(novel_id: int, session: Session = Depends(get_session)) -> CheckReportResponse:
    report = session.exec(
        select(CheckReport).where(CheckReport.novel_id == novel_id).order_by(CheckReport.created_at.desc())
    ).first()
    if not report:
        return CheckReportResponse(issues=[])

    issues = _safe_json_loads(report.issues_json, [])
    return CheckReportResponse(issues=[CheckIssueResponse(**_normalize_issue(issue)) for issue in issues])


def _normalize_issue(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "level": str(item.get("level", "low")),
        "type": str(item.get("type", "未知问题")),
        "scene_id": _safe_int(item.get("scene_id"), 0),
        "description": str(item.get("description", "")),
        "suggestion": str(item.get("suggestion", "")),
    }


def _format_characters(characters: list[Character]) -> str:
    if not characters:
        return "暂无人物档案"
    return "\n".join(f"- {item.name}：{item.role}；目标：{item.goal}；证据：{item.evidence}" for item in characters)


def _format_scenes(scenes: list[Scene]) -> str:
    if not scenes:
        return "暂无分场大纲"
    return "\n".join(
        f"- 第 {item.scene_index} 场 {item.title}：{item.time} / {item.location}；人物：{item.characters_json}；冲突：{item.conflict}"
        for item in scenes
    )


def _format_scripts(scripts: list[Script]) -> str:
    if not scripts:
        return "暂无已生成剧本"

    latest_scripts: dict[int, Script] = {}
    for script in scripts:
        latest_scripts[script.scene_id] = script
    return "\n\n".join(f"场景 {script.scene_id} v{script.version}：\n{script.content}" for script in latest_scripts.values())


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_json_loads(value: str, default: list) -> list:
    try:
        loaded = json.loads(value)
        return loaded if isinstance(loaded, list) else default
    except json.JSONDecodeError:
        return default
