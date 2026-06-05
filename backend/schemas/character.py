from pydantic import BaseModel


class CharacterRelation(BaseModel):
    target: str
    relation: str


class CharacterResponse(BaseModel):
    id: int
    name: str
    role: str
    personality: list[str]
    goal: str
    first_appearance: str
    relations: list[CharacterRelation]
    evidence: str


class CharacterListResponse(BaseModel):
    characters: list[CharacterResponse]
