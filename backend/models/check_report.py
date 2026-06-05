from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class CheckReport(SQLModel, table=True):
    __tablename__ = "check_reports"

    id: Optional[int] = Field(default=None, primary_key=True)
    novel_id: int = Field(index=True)
    issues_json: str = "[]"
    created_at: datetime = Field(default_factory=datetime.utcnow)
