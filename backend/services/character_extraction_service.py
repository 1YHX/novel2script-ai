import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from models.character import Character
from models.chapter import Chapter
from models.novel import Novel
from services.llm_service import LLMError, LLMService


BATCH_CHAPTER_COUNT = 5
MAX_BATCH_CHARS = 12000
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "character_extract.txt"


@dataclass
class CharacterCandidate:
    name: str
    role: str = "未知"
    personality: list[str] = field(default_factory=list)
    goal: str = "未知"
    first_appearance: str = "未知"
    relations: list[dict[str, str]] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    appeared_chapters: set[int] = field(default_factory=set)
    key_event_hits: int = 0


class CharacterExtractionService:
    def __init__(self, llm_service: Optional[LLMService] = None) -> None:
        self.llm_service = llm_service or LLMService()
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    def extract(self, novel: Novel, chapters: list[Chapter]) -> list[Character]:
        candidates: dict[str, CharacterCandidate] = {}

        for batch in self._batch_chapters(chapters):
            result = self.llm_service.generate_json(self.system_prompt, self._build_batch_prompt(novel, batch), "characters")
            raw_characters = result.get("characters")
            if not isinstance(raw_characters, list):
                raise LLMError("人物抽取结果缺少 characters 数组")

            for item in raw_characters:
                if isinstance(item, dict):
                    self._merge_candidate(candidates, item, batch)

        selected = [candidate for candidate in candidates.values() if self._should_keep(candidate)]
        selected.sort(key=lambda item: (min(item.appeared_chapters or {999999}), -len(item.appeared_chapters), item.name))
        return [self._to_model(novel.id, candidate) for candidate in selected]

    def _batch_chapters(self, chapters: list[Chapter]) -> list[list[Chapter]]:
        batches: list[list[Chapter]] = []
        current: list[Chapter] = []
        current_chars = 0

        for chapter in chapters:
            chapter_len = len(chapter.content or "")
            if current and (len(current) >= BATCH_CHAPTER_COUNT or current_chars + chapter_len > MAX_BATCH_CHARS):
                batches.append(current)
                current = []
                current_chars = 0

            current.append(chapter)
            current_chars += chapter_len

        if current:
            batches.append(current)
        return batches

    def _build_batch_prompt(self, novel: Novel, chapters: list[Chapter]) -> str:
        chapter_blocks = []
        for chapter in chapters:
            content = self._compact(chapter.content, 3200)
            chapter_blocks.append(f"## 第{chapter.order_index}章 {chapter.title}\n{content}")

        return "\n\n".join(
            [
                f"小说标题：{novel.title}",
                "本次只分析下面这一批章节。请提取本批出现的人物候选，并判断其是否参与主线或关键事件。",
                "章节正文：",
                "\n\n".join(chapter_blocks),
            ]
        )

    def _merge_candidate(
        self,
        candidates: dict[str, CharacterCandidate],
        item: dict[str, Any],
        batch: list[Chapter],
    ) -> None:
        name = self._clean_name(item.get("name"))
        if not name:
            return

        candidate = candidates.setdefault(name, CharacterCandidate(name=name))
        candidate.role = self._prefer_text(candidate.role, item.get("role"))
        candidate.goal = self._prefer_text(candidate.goal, item.get("goal"))

        for personality in self._ensure_string_list(item.get("personality")):
            if personality not in candidate.personality:
                candidate.personality.append(personality)

        candidate.relations = self._merge_relations(candidate.relations, self._ensure_relations(item.get("relations")))

        batch_chapter_indexes = {chapter.order_index for chapter in batch}
        item_chapters = self._ensure_int_set(item.get("appeared_chapters")) or self._infer_chapters_for_name(name, batch)
        candidate.appeared_chapters.update(item_chapters or batch_chapter_indexes)

        first_appearance = self._clean_text(item.get("first_appearance"))
        if first_appearance and (candidate.first_appearance == "未知" or self._first_chapter_index(first_appearance) < self._first_chapter_index(candidate.first_appearance)):
            candidate.first_appearance = first_appearance

        evidence = self._clean_text(item.get("evidence"))
        if evidence and evidence not in candidate.evidence:
            candidate.evidence.append(evidence)

        if self._is_key_event_candidate(item, batch, name):
            candidate.key_event_hits += 1

    def _should_keep(self, candidate: CharacterCandidate) -> bool:
        if len(candidate.appeared_chapters) >= 2:
            return True
        if candidate.key_event_hits > 0:
            return True
        if any(keyword in candidate.role for keyword in ["主角", "男主", "女主", "反派", "关键", "核心", "线索"]):
            return True
        if any(keyword in candidate.goal for keyword in ["真相", "复仇", "逃", "寻找", "保护", "阻止", "拯救", "调查"]):
            return True
        return False

    def _to_model(self, novel_id: int, candidate: CharacterCandidate) -> Character:
        evidence = "；".join(candidate.evidence[:3])
        appeared = "、".join(f"第{index}章" for index in sorted(candidate.appeared_chapters))
        if appeared:
            evidence = f"{evidence}（出现章节：{appeared}）" if evidence else f"出现章节：{appeared}"

        return Character(
            novel_id=novel_id,
            name=candidate.name,
            role=candidate.role or "未知",
            personality_json=json.dumps(candidate.personality[:8] or ["未知"], ensure_ascii=False),
            goal=candidate.goal or "未知",
            first_appearance=candidate.first_appearance or "未知",
            relations_json=json.dumps(candidate.relations, ensure_ascii=False),
            evidence=evidence,
        )

    def _is_key_event_candidate(self, item: dict[str, Any], batch: list[Chapter], name: str) -> bool:
        raw_importance = " ".join(
            [
                self._clean_text(item.get("importance")),
                self._clean_text(item.get("mainline_role")),
                self._clean_text(item.get("evidence")),
                self._clean_text(item.get("goal")),
                self._clean_text(item.get("role")),
            ]
        )
        if any(keyword in raw_importance for keyword in ["主线", "关键", "转折", "真相", "冲突", "危机", "反派", "主角"]):
            return True

        chapter_text = "\n".join(chapter.content or "" for chapter in batch if name in (chapter.content or ""))
        return any(keyword in chapter_text for keyword in ["秘密", "真相", "危险", "死亡", "威胁", "身份", "系统", "任务", "逃", "杀"])

    def _infer_chapters_for_name(self, name: str, batch: list[Chapter]) -> set[int]:
        return {chapter.order_index for chapter in batch if name in (chapter.content or "")}

    def _merge_relations(
        self,
        current: list[dict[str, str]],
        incoming: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        seen = {(item.get("target", ""), item.get("relation", "")) for item in current}
        for item in incoming:
            key = (item.get("target", ""), item.get("relation", ""))
            if key not in seen:
                current.append(item)
                seen.add(key)
        return current[:12]

    def _prefer_text(self, current: str, incoming: Any) -> str:
        text = self._clean_text(incoming)
        if not text:
            return current
        if current == "未知" or len(text) > len(current):
            return text
        return current

    def _clean_name(self, value: Any) -> str:
        text = self._clean_text(value)
        if not text or text in {"未知", "无", "群众", "众人", "路人"}:
            return ""
        return re.sub(r"[，。！？；：、“”\"'（）()《》\s]", "", text)[:20]

    def _clean_text(self, value: Any) -> str:
        if value is None:
            return ""
        return re.sub(r"\s+", " ", str(value)).strip()

    def _compact(self, text: str, limit: int) -> str:
        return re.sub(r"\s+", " ", text or "").strip()[:limit]

    def _ensure_string_list(self, value: Any) -> list[str]:
        if isinstance(value, list):
            return [self._clean_text(item) for item in value if self._clean_text(item)]
        text = self._clean_text(value)
        return [text] if text else []

    def _ensure_relations(self, value: Any) -> list[dict[str, str]]:
        if not isinstance(value, list):
            return []

        relations: list[dict[str, str]] = []
        for item in value:
            if isinstance(item, dict):
                target = self._clean_text(item.get("target"))
                relation = self._clean_text(item.get("relation"))
                if target and relation:
                    relations.append({"target": target, "relation": relation})
        return relations

    def _ensure_int_set(self, value: Any) -> set[int]:
        if not isinstance(value, list):
            return set()
        numbers = set()
        for item in value:
            match = re.search(r"\d+", str(item))
            if match:
                numbers.add(int(match.group(0)))
        return numbers

    def _first_chapter_index(self, text: str) -> int:
        match = re.search(r"\d+", text)
        return int(match.group(0)) if match else 999999
