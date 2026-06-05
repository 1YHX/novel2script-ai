import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, delete, select

from database import get_session
from models.character import Character
from models.novel import Novel
from schemas.character import CharacterListResponse, CharacterRelation, CharacterResponse
from services.llm_service import LLMError, LLMService


router = APIRouter(prefix="/api/characters", tags=["characters"])
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "character_extract.txt"


@router.post("/extract/{novel_id}", response_model=CharacterListResponse)
def extract_characters(novel_id: int, session: Session = Depends(get_session)) -> CharacterListResponse:
    novel = session.get(Novel, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    user_prompt = f"小说标题：{novel.title}\n\n小说正文：\n{novel.content[:12000]}"

    try:
        result = LLMService().generate_json(system_prompt, user_prompt, "characters")
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    raw_characters = result.get("characters")
    if not isinstance(raw_characters, list):
        raise HTTPException(status_code=502, detail="人物抽取结果缺少 characters 数组")

    session.exec(delete(Character).where(Character.novel_id == novel_id))
    session.commit()

    saved_characters: list[Character] = []
    for item in raw_characters:
        if not isinstance(item, dict) or not item.get("name"):
            continue

        character = Character(
            novel_id=novel_id,
            name=str(item.get("name", "未知")),
            role=str(item.get("role", "未知")),
            personality_json=json.dumps(_ensure_string_list(item.get("personality")), ensure_ascii=False),
            goal=str(item.get("goal", "未知")),
            first_appearance=str(item.get("first_appearance", "未知")),
            relations_json=json.dumps(_ensure_relations(item.get("relations")), ensure_ascii=False),
            evidence=str(item.get("evidence", "")),
        )
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


def _ensure_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if value:
        return [str(value)]
    return ["未知"]


def _ensure_relations(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []

    relations: list[dict[str, str]] = []
    for item in value:
        if isinstance(item, dict):
            relations.append(
                {
                    "target": str(item.get("target", "未知")),
                    "relation": str(item.get("relation", "未知")),
                }
            )
    return relations


def _safe_json_loads(value: str, default: Any) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default
