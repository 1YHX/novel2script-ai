from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from database import get_session
from models.chapter import Chapter
from models.novel import Novel
from models.paragraph import Paragraph
from schemas.novel import ChapterResponse, NovelImportRequest, NovelImportResponse, ParagraphResponse
from services.parser_service import ParserService


router = APIRouter(prefix="/api/novels", tags=["novels"])


@router.post("/import", response_model=NovelImportResponse)
def import_novel(payload: NovelImportRequest, session: Session = Depends(get_session)) -> NovelImportResponse:
    title = payload.title.strip()
    content = payload.content.strip()

    if not title:
        raise HTTPException(status_code=400, detail="项目标题不能为空")
    if not content:
        raise HTTPException(status_code=400, detail="小说正文不能为空")

    parsed_chapters = ParserService().parse(content)
    if not parsed_chapters:
        raise HTTPException(status_code=400, detail="未解析到有效正文")

    novel = Novel(title=title, content=content)
    session.add(novel)
    session.commit()
    session.refresh(novel)

    response_chapters: list[ChapterResponse] = []
    paragraph_count = 0

    for chapter_index, parsed_chapter in enumerate(parsed_chapters, start=1):
        chapter = Chapter(
            novel_id=novel.id,
            title=parsed_chapter.title,
            order_index=chapter_index,
            content=parsed_chapter.content,
        )
        session.add(chapter)
        session.commit()
        session.refresh(chapter)

        paragraph_responses: list[ParagraphResponse] = []
        for paragraph_index, parsed_paragraph in enumerate(parsed_chapter.paragraphs, start=1):
            paragraph = Paragraph(
                novel_id=novel.id,
                chapter_id=chapter.id,
                order_index=paragraph_index,
                content=parsed_paragraph.content,
            )
            session.add(paragraph)
            session.commit()
            session.refresh(paragraph)
            paragraph_count += 1
            paragraph_responses.append(ParagraphResponse(paragraph_id=paragraph.id, content=paragraph.content))

        response_chapters.append(
            ChapterResponse(chapter_id=chapter.id, title=chapter.title, paragraphs=paragraph_responses)
        )

    return NovelImportResponse(
        novel_id=novel.id,
        title=novel.title,
        chapter_count=len(response_chapters),
        paragraph_count=paragraph_count,
        chapters=response_chapters,
    )
