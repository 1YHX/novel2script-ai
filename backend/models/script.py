from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Script(SQLModel, table=True):
    __tablename__ = "scripts"

    id: Optional[int] = Field(default=None, primary_key=True)
    novel_id: int = Field(index=True)
    scene_id: int = Field(index=True)
    content: str
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
