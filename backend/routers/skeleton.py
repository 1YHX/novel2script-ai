from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models.character import Character
from models.chapter import Chapter
from models.novel import Novel
from models.story_skeleton import StorySkeleton
from schemas.skeleton import SkeletonResponse
from services.story_skeleton_service import StorySkeletonService


router = APIRouter(prefix="/api/skeletons", tags=["skeletons"])


@router.post("/generate/{novel_id}", response_model=SkeletonResponse)
def generate_skeleton(novel_id: int, session: Session = Depends(get_session)) -> SkeletonResponse:
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    chapters = session.exec(select(Chapter).where(Chapter.novel_id == novel_id).order_by(Chapter.order_index)).all()
    characters = session.exec(select(Character).where(Character.novel_id == novel_id).order_by(Character.id)).all()
    content = StorySkeletonService().generate(novel, chapters, characters)
    skeleton = StorySkeleton(novel_id=novel_id, content=content)
    session.add(skeleton)
    session.commit()
    session.refresh(skeleton)
    return _to_response(skeleton)


@router.get("/{novel_id}", response_model=SkeletonResponse)
def get_skeleton(novel_id: int, session: Session = Depends(get_session)) -> SkeletonResponse:
    skeleton = session.exec(
        select(StorySkeleton).where(StorySkeleton.novel_id == novel_id).order_by(StorySkeleton.created_at.desc())
    ).first()
    if not skeleton:
        raise HTTPException(status_code=404, detail="故事骨架不存在")
    return _to_response(skeleton)


def _to_response(skeleton: StorySkeleton) -> SkeletonResponse:
    return SkeletonResponse(skeleton_id=skeleton.id, novel_id=skeleton.novel_id, content=skeleton.content)
