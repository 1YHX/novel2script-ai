import json
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
from services.consistency_service import ConsistencyService


router = APIRouter(prefix="/api/check", tags=["check"])


@router.post("/consistency/{novel_id}", response_model=CheckReportResponse)
def run_consistency_check(novel_id: int, session: Session = Depends(get_session)) -> CheckReportResponse:
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    characters = session.exec(select(Character).where(Character.novel_id == novel_id).order_by(Character.id)).all()
    scenes = session.exec(select(Scene).where(Scene.novel_id == novel_id).order_by(Scene.scene_index)).all()
    scripts = session.exec(select(Script).where(Script.novel_id == novel_id).order_by(Script.scene_id, Script.version)).all()

    issues = ConsistencyService().check(characters=characters, scenes=scenes, scripts=scripts)
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
