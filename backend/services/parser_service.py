import re
from dataclasses import dataclass


CHAPTER_PATTERN = re.compile(
    r"^\s*((第[一二三四五六七八九十百千万\d]+章|Chapter\s+\d+|[一二三四五六七八九十]+、).*)\s*$",
    re.IGNORECASE,
)


@dataclass
class ParsedParagraph:
    content: str


@dataclass
class ParsedChapter:
    title: str
    paragraphs: list[ParsedParagraph]

    @property
    def content(self) -> str:
        return "\n\n".join(paragraph.content for paragraph in self.paragraphs)


class ParserService:
    def parse(self, content: str) -> list[ParsedChapter]:
        normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip()
        if not normalized:
            return []

        blocks = [block.strip() for block in re.split(r"\n\s*\n", normalized) if block.strip()]
        chapters: list[ParsedChapter] = []
        current_title = "正文"
        current_paragraphs: list[ParsedParagraph] = []

        for block in blocks:
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            first_line = lines[0] if lines else ""

            if len(lines) == 1 and CHAPTER_PATTERN.match(first_line):
                if current_paragraphs:
                    chapters.append(ParsedChapter(title=current_title, paragraphs=current_paragraphs))
                current_title = first_line
                current_paragraphs = []
                continue

            if CHAPTER_PATTERN.match(first_line) and len(lines) > 1:
                if current_paragraphs:
                    chapters.append(ParsedChapter(title=current_title, paragraphs=current_paragraphs))
                current_title = first_line
                current_paragraphs = [ParsedParagraph(content="\n".join(lines[1:]))]
                continue

            current_paragraphs.append(ParsedParagraph(content=block))

        if current_paragraphs:
            chapters.append(ParsedChapter(title=current_title, paragraphs=current_paragraphs))

        if len(chapters) == 1 and chapters[0].title == "正文" and len(chapters[0].paragraphs) > 8:
            return self._group_without_chapter_titles(chapters[0].paragraphs)

        return chapters

    def _group_without_chapter_titles(self, paragraphs: list[ParsedParagraph]) -> list[ParsedChapter]:
        group_size = 6
        grouped: list[ParsedChapter] = []
        for index in range(0, len(paragraphs), group_size):
            group = paragraphs[index : index + group_size]
            grouped.append(ParsedChapter(title=f"自动分组 {len(grouped) + 1}", paragraphs=group))
        return grouped
