from typing import Optional

from sqlmodel import Field, SQLModel


class Scene(SQLModel, table=True):
    __tablename__ = "scenes"

    id: Optional[int] = Field(default=None, primary_key=True)
    novel_id: int = Field(index=True)
    scene_index: int
    title: str
    time: str = "未知"
    location: str = "未知"
    characters_json: str = "[]"
    plot_goal: str = ""
    conflict: str = ""
    source_paragraphs_json: str = "[]"
