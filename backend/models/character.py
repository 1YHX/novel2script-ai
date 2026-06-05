from typing import Optional

from sqlmodel import Field, SQLModel


class Character(SQLModel, table=True):
    __tablename__ = "characters"

    id: Optional[int] = Field(default=None, primary_key=True)
    novel_id: int = Field(index=True)
    name: str
    role: str = "未知"
    personality_json: str = "[]"
    goal: str = "未知"
    first_appearance: str = "未知"
    relations_json: str = "[]"
    evidence: str = ""
