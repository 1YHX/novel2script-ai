from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models.adaptation_strategy import AdaptationStrategy
from models.character import Character
from models.chapter import Chapter
from models.novel import Novel
from schemas.strategy import StrategyResponse
from services.adaptation_strategy_service import AdaptationStrategyService


router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.post("/generate/{novel_id}", response_model=StrategyResponse)
def generate_strategy(novel_id: int, session: Session = Depends(get_session)) -> StrategyResponse:
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    chapters = session.exec(select(Chapter).where(Chapter.novel_id == novel_id).order_by(Chapter.order_index)).all()
    characters = session.exec(select(Character).where(Character.novel_id == novel_id).order_by(Character.id)).all()
    content = AdaptationStrategyService().generate(novel, chapters, characters)
    strategy = AdaptationStrategy(novel_id=novel_id, content=content)
    session.add(strategy)
    session.commit()
    session.refresh(strategy)
    return _to_response(strategy)


@router.get("/{novel_id}", response_model=StrategyResponse)
def get_strategy(novel_id: int, session: Session = Depends(get_session)) -> StrategyResponse:
    strategy = session.exec(
        select(AdaptationStrategy)
        .where(AdaptationStrategy.novel_id == novel_id)
        .order_by(AdaptationStrategy.created_at.desc())
    ).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="改编策略不存在")
    return _to_response(strategy)


def _to_response(strategy: AdaptationStrategy) -> StrategyResponse:
    return StrategyResponse(strategy_id=strategy.id, novel_id=strategy.novel_id, content=strategy.content)
