import json

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select

from database import get_session
from models.character import Character
from models.check_report import CheckReport
from models.chapter import Chapter
from models.novel import Novel
from models.scene import Scene
from models.script import Script
from services.export_service import ExportService


router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/markdown/{novel_id}")
def export_markdown(novel_id: int, session: Session = Depends(get_session)) -> Response:
    novel, characters, chapters, scenes, latest_scripts, issues = _load_export_data(novel_id, session)
    markdown = ExportService().build_markdown(
        title=novel.title,
        characters=characters,
        scenes=scenes,
        scripts=list(latest_scripts.values()),
        issues=issues,
    )

    filename = f"novel2script-{novel_id}.md"
    return Response(
        content=markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/yaml/{novel_id}")
def export_yaml(novel_id: int, session: Session = Depends(get_session)) -> Response:
    novel, characters, chapters, scenes, latest_scripts, issues = _load_export_data(novel_id, session)
    yaml_content = ExportService().build_yaml(
        title=novel.title,
        novel_id=novel.id,
        chapter_count=len(chapters),
        characters=characters,
        scenes=scenes,
        scripts=list(latest_scripts.values()),
        issues=issues,
    )

    filename = f"novel2script-{novel_id}.yaml"
    return Response(
        content=yaml_content,
        media_type="application/yaml; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _load_export_data(novel_id: int, session: Session):
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    characters = session.exec(select(Character).where(Character.novel_id == novel_id).order_by(Character.id)).all()
    chapters = session.exec(select(Chapter).where(Chapter.novel_id == novel_id).order_by(Chapter.order_index)).all()
    scenes = session.exec(select(Scene).where(Scene.novel_id == novel_id).order_by(Scene.scene_index)).all()
    scripts = session.exec(select(Script).where(Script.novel_id == novel_id).order_by(Script.scene_id, Script.version)).all()
    report = session.exec(
        select(CheckReport).where(CheckReport.novel_id == novel_id).order_by(CheckReport.created_at.desc())
    ).first()

    latest_scripts: dict[int, Script] = {}
    for script in scripts:
        latest_scripts[script.scene_id] = script

    return novel, characters, chapters, scenes, latest_scripts, _safe_json_loads(report.issues_json, []) if report else []


def _safe_json_loads(value: str, default: list) -> list:
    try:
        loaded = json.loads(value)
        return loaded if isinstance(loaded, list) else default
    except json.JSONDecodeError:
        return default
