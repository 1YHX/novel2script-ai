import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, delete, select

from database import get_session
from models.character import Character
from models.chapter import Chapter
from models.novel import Novel
from schemas.character import CharacterListResponse, CharacterRelation, CharacterResponse
from services.llm_service import LLMError, LLMService
from services.character_extraction_service import CharacterExtractionService


router = APIRouter(prefix="/api/characters", tags=["characters"])


@router.post("/extract/{novel_id}", response_model=CharacterListResponse)
def extract_characters(novel_id: int, session: Session = Depends(get_session)) -> CharacterListResponse:
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    try:
        chapters = session.exec(select(Chapter).where(Chapter.novel_id == novel_id).order_by(Chapter.order_index)).all()
        character_models = CharacterExtractionService(LLMService()).extract(novel, chapters)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    session.exec(delete(Character).where(Character.novel_id == novel_id))
    session.commit()

    saved_characters: list[Character] = []
    for character in character_models:
        session.add(character)
        saved_characters.append(character)

    session.commit()
    for character in saved_characters:
        session.refresh(character)

    return CharacterListResponse(characters=[_to_response(character) for character in saved_characters])


@router.get("/{novel_id}", response_model=CharacterListResponse)
def get_characters(novel_id: int, session: Session = Depends(get_session)) -> CharacterListResponse:
    characters = session.exec(select(Character).where(Character.novel_id == novel_id).order_by(Character.id)).all()
    return CharacterListResponse(characters=[_to_response(character) for character in characters])


def _to_response(character: Character) -> CharacterResponse:
    relations = [
        CharacterRelation(target=str(item.get("target", "未知")), relation=str(item.get("relation", "未知")))
        for item in _safe_json_loads(character.relations_json, [])
        if isinstance(item, dict)
    ]
    return CharacterResponse(
        id=character.id,
        name=character.name,
        role=character.role,
        personality=_safe_json_loads(character.personality_json, []),
        goal=character.goal,
        first_appearance=character.first_appearance,
        relations=relations,
        evidence=character.evidence,
    )


def _safe_json_loads(value: str, default: Any) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default
