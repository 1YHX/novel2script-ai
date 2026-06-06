from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select

from database import get_session
from models.adaptation_strategy import AdaptationStrategy
from models.character import Character
from models.chapter import Chapter
from models.novel import Novel
from models.scene import Scene
from models.script import Script
from models.story_skeleton import StorySkeleton
from services.export_service import ExportService


router = APIRouter(prefix="/api/export", tags=["export"])
MIN_REQUIRED_CHAPTERS = 3


@router.get("/markdown/{novel_id}")
def export_markdown(novel_id: int, session: Session = Depends(get_session)) -> Response:
    novel, characters, chapters, scenes, latest_scripts, skeleton, strategy = _load_export_data(novel_id, session)
    _ensure_minimum_chapters(chapters)
    markdown = ExportService().build_markdown(
        title=novel.title,
        skeleton=skeleton.content if skeleton else "",
        strategy=strategy.content if strategy else "",
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


@router.get("/yaml/{novel_id}")
def export_yaml(novel_id: int, session: Session = Depends(get_session)) -> Response:
    novel, characters, chapters, scenes, latest_scripts, skeleton, strategy = _load_export_data(novel_id, session)
    _ensure_minimum_chapters(chapters)
    yaml_content = ExportService().build_yaml(
        title=novel.title,
        novel_id=novel.id,
        chapter_count=len(chapters),
        skeleton=skeleton.content if skeleton else "",
        strategy=strategy.content if strategy else "",
        characters=characters,
        scenes=scenes,
        scripts=list(latest_scripts.values()),
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
    strategy = session.exec(
        select(AdaptationStrategy)
        .where(AdaptationStrategy.novel_id == novel_id)
        .order_by(AdaptationStrategy.created_at.desc())
    ).first()
    skeleton = session.exec(
        select(StorySkeleton).where(StorySkeleton.novel_id == novel_id).order_by(StorySkeleton.created_at.desc())
    ).first()
    latest_scripts: dict[int, Script] = {}
    for script in scripts:
        latest_scripts[script.scene_id] = script

    return novel, characters, chapters, scenes, latest_scripts, skeleton, strategy


def _ensure_minimum_chapters(chapters: list[Chapter]) -> None:
    if len(chapters) < MIN_REQUIRED_CHAPTERS:
        raise HTTPException(
            status_code=400,
            detail=f"题目要求至少 {MIN_REQUIRED_CHAPTERS} 个章节，当前项目只有 {len(chapters)} 章，无法导出",
        )
