from typing import Optional

from sqlmodel import Field, SQLModel


class Chapter(SQLModel, table=True):
    __tablename__ = "chapters"

    id: Optional[int] = Field(default=None, primary_key=True)
    novel_id: int = Field(index=True)
    title: str
    order_index: int
    content: str
