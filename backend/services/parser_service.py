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

        chapters: list[ParsedChapter] = []
        current_title = "正文"
        current_paragraphs: list[ParsedParagraph] = []
        pending_lines: list[str] = []

        def flush_pending() -> None:
            if pending_lines:
                current_paragraphs.append(ParsedParagraph(content="\n".join(pending_lines).strip()))
                pending_lines.clear()

        for raw_line in normalized.split("\n"):
            line = raw_line.strip()
            if not line:
                flush_pending()
                continue

            if self._is_chapter_title(line):
                flush_pending()
                if current_paragraphs:
                    chapters.append(ParsedChapter(title=current_title, paragraphs=current_paragraphs))
                current_title = line
                current_paragraphs = []
                continue

            if self._looks_like_dialogue_or_paragraph(line):
                flush_pending()
                current_paragraphs.append(ParsedParagraph(content=line))
            else:
                pending_lines.append(line)

        flush_pending()
        if current_paragraphs:
            chapters.append(ParsedChapter(title=current_title, paragraphs=current_paragraphs))

        if len(chapters) == 1 and chapters[0].title == "正文" and len(chapters[0].paragraphs) > 8:
            return self._group_without_chapter_titles(chapters[0].paragraphs)

        return chapters

    def _looks_like_dialogue_or_paragraph(self, line: str) -> bool:
        if len(line) >= 18:
            return True
        if line.endswith(("。", "！", "？", "……", "\"", "”")):
            return True
        if "：" in line or ":" in line:
            return True
        return False

    def _is_chapter_title(self, line: str) -> bool:
        if not CHAPTER_PATTERN.match(line):
            return False
        if re.match(r"^\s*(第[一二三四五六七八九十百千万\d]+章|Chapter\s+\d+)", line, re.IGNORECASE):
            return len(line) <= 80
        if re.match(r"^\s*[一二三四五六七八九十]+、", line):
            return len(line) <= 30
        return False

    def _group_without_chapter_titles(self, paragraphs: list[ParsedParagraph]) -> list[ParsedChapter]:
        group_size = 6
        grouped: list[ParsedChapter] = []
        for index in range(0, len(paragraphs), group_size):
            group = paragraphs[index : index + group_size]
            grouped.append(ParsedChapter(title=f"自动分组 {len(grouped) + 1}", paragraphs=group))
        return grouped
