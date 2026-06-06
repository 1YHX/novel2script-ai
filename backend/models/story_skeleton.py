from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class StorySkeleton(SQLModel, table=True):
    __tablename__ = "story_skeletons"

    id: Optional[int] = Field(default=None, primary_key=True)
    novel_id: int = Field(index=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
