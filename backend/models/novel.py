from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Novel(SQLModel, table=True):
    __tablename__ = "novels"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
