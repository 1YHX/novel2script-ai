from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select

from database import get_session
from models.character import Character
from models.novel import Novel
from models.scene import Scene
from models.script import Script
from services.export_service import ExportService


router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/markdown/{novel_id}")
def export_markdown(novel_id: int, session: Session = Depends(get_session)) -> Response:
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    characters = session.exec(select(Character).where(Character.novel_id == novel_id).order_by(Character.id)).all()
    scenes = session.exec(select(Scene).where(Scene.novel_id == novel_id).order_by(Scene.scene_index)).all()
    scripts = session.exec(select(Script).where(Script.novel_id == novel_id).order_by(Script.scene_id, Script.version)).all()

    latest_scripts: dict[int, Script] = {}
    for script in scripts:
        latest_scripts[script.scene_id] = script

    markdown = ExportService().build_markdown(
        title=novel.title,
        characters=characters,
        scenes=scenes,
        scripts=list(latest_scripts.values()),
    )

    filename = f"novel2script-{novel_id}.md"
    return Response(
        content=markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
