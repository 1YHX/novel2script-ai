from pathlib import Path
from typing import Generator

from sqlmodel import SQLModel, Session, create_engine

from config import get_settings
from models.chapter import Chapter  # noqa: F401
from models.character import Character  # noqa: F401
from models.novel import Novel  # noqa: F401
from models.paragraph import Paragraph  # noqa: F401
from models.scene import Scene  # noqa: F401
from models.script import Script  # noqa: F401


settings = get_settings()
db_path = settings.database_url.replace("sqlite:///", "")
Path(db_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(settings.database_url, echo=False, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
