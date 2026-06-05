from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class NovelImportRequest(BaseModel):
    title: str
    content: str


class ParagraphResponse(BaseModel):
    paragraph_id: int
    content: str


class ChapterResponse(BaseModel):
    chapter_id: int
    title: str
    paragraphs: list[ParagraphResponse]


class NovelImportResponse(BaseModel):
    novel_id: int
    title: str
    chapter_count: int
    paragraph_count: int
    chapters: list[ChapterResponse]


class NovelSummaryResponse(BaseModel):
    novel_id: int
    title: str
    chapter_count: int
    paragraph_count: int
    scene_count: int
    script_count: int


class NovelListResponse(BaseModel):
    novels: list[NovelSummaryResponse]
