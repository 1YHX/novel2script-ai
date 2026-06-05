from typing import Optional

from sqlmodel import Field, SQLModel


class Paragraph(SQLModel, table=True):
    __tablename__ = "paragraphs"

    id: Optional[int] = Field(default=None, primary_key=True)
    novel_id: int = Field(index=True)
    chapter_id: int = Field(index=True)
    order_index: int
    content: str
