import json
import re
from typing import Any, Optional

from models.character import Character
from models.chapter import Chapter
from models.novel import Novel
from models.paragraph import Paragraph
from services.llm_service import LLMError, LLMService


class ScenePlannerService:
    def __init__(self, llm_service: Optional[LLMService] = None) -> None:
        self.llm_service = llm_service or LLMService()

    def plan(
        self,
        novel: Novel,
        chapters: list[Chapter],
        paragraphs: list[Paragraph],
        characters: list[Character],
        system_prompt: str,
        scene_count: int,
    ) -> list[dict[str, Any]]:
        if not paragraphs:
            return []

        user_prompt = self._build_user_prompt(novel, chapters, paragraphs, characters, scene_count)
        try:
            result = self.llm_service.generate_json(system_prompt, user_prompt, "scenes")
            scenes = self._normalize_scenes(result.get("scenes"), scene_count, paragraphs, characters)
            if scenes:
                return scenes
        except LLMError:
            pass

        return self._fallback_plan(scene_count, paragraphs, characters)

    def _build_user_prompt(
        self,
        novel: Novel,
        chapters: list[Chapter],
        paragraphs: list[Paragraph],
        characters: list[Character],
        scene_count: int,
    ) -> str:
        paragraph_lines = []
        for paragraph in paragraphs[:120]:
            text = self._compact(paragraph.content, 220)
            paragraph_lines.append(f"[P{paragraph.id}] {text}")

        character_lines = []
        for character in characters:
            personality = "、".join(self._loads(character.personality_json, []))
            relations = self._loads(character.relations_json, [])
            relation_text = "；".join(
                f"{item.get('target', '未知')}:{item.get('relation', '未知')}"
                for item in relations
                if isinstance(item, dict)
            )
            character_lines.append(
                f"- {character.name}｜{character.role}｜性格：{personality or '未知'}｜目标：{character.goal}｜关系：{relation_text or '未知'}"
            )

        return "\n\n".join(
            [
                f"小说标题：{novel.title}",
                f"目标场景数量：{scene_count}",
                "改编方法：参考 Toonflow 的分层思路，先阅读章节事件表，建立全局故事走向，再把相邻剧情节点合并为可拍摄分场。每一场必须推进人物目标或制造冲突。",
                "章节事件表：\n" + self._build_chapter_event_table(chapters, characters),
                "人物档案：\n" + ("\n".join(character_lines) if character_lines else "暂无人物档案，请从段落中识别主要人物。"),
                "带编号的小说段落。source_paragraphs 必须只使用这些 P 后面的数字：\n" + "\n".join(paragraph_lines),
                "请输出 scenes JSON。不要只改编开头段落，要结合章节事件表覆盖主要剧情阶段；不要把章节标题当作场景标题，场景标题要像影视分场，例如“码头密信”“灯塔暗号”。",
            ]
        )

    def _build_chapter_event_table(self, chapters: list[Chapter], characters: list[Character]) -> str:
        if not chapters:
            return "暂无章节事件表。"

        lines = ["| 章节 | 涉及角色 | 核心事件 | 主线关系 | 信息密度 | 情绪强度 |", "|---|---|---|---|---|---|"]
        for chapter in chapters[:80]:
            text = self._compact(chapter.content, 360)
            involved = [character.name for character in characters if character.name and character.name in text]
            if not involved:
                involved = self._infer_names_from_text(text)
            event = self._compact(re.sub(r"\s+", "", text), 70) or "章节事件待提炼"
            lines.append(
                "| {chapter} | {roles} | {event} | {mainline} | {density} | {emotion} |".format(
                    chapter=f"第{chapter.order_index}章 {chapter.title}",
                    roles="、".join(involved[:5]) or "未知",
                    event=event,
                    mainline=self._mainline_weight(text),
                    density=self._information_density(text),
                    emotion=self._emotion_tags(text),
                )
            )
        return "\n".join(lines)

    def _infer_names_from_text(self, text: str) -> list[str]:
        candidates = re.findall(r"[\u4e00-\u9fa5]{2,4}", text)
        stop_words = {"第一章", "第二章", "第三章", "第四章", "一个", "他们", "自己", "父亲", "小说", "时候", "什么"}
        names = []
        for candidate in candidates:
            if candidate in stop_words:
                continue
            if candidate not in names:
                names.append(candidate)
            if len(names) >= 3:
                break
        return names

    def _mainline_weight(self, text: str) -> str:
        if any(keyword in text for keyword in ["目标", "秘密", "真相", "危险", "死亡", "威胁", "身份", "系统", "任务"]):
            return "强（直接推动主线）"
        if any(keyword in text for keyword in ["回忆", "关系", "解释", "线索", "准备"]):
            return "中（补充线索关系）"
        return "弱（过渡或氛围）"

    def _information_density(self, text: str) -> str:
        if len(text) >= 900:
            return "高"
        if len(text) >= 360:
            return "中"
        return "低"

    def _emotion_tags(self, text: str) -> str:
        tags = []
        mapping = [
            ("冲突", ["争", "吵", "怒", "拒绝", "威胁"]),
            ("悬疑", ["秘密", "真相", "线索", "谜", "暗号"]),
            ("危险", ["死", "血", "枪", "逃", "危险", "杀"]),
            ("转折", ["突然", "却", "但是", "没想到"]),
            ("情感", ["哭", "母亲", "父亲", "爱", "痛苦"]),
        ]
        for tag, keywords in mapping:
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
        return "+".join(tags[:3]) or "平铺"

    def _normalize_scenes(
        self,
        raw_scenes: Any,
        scene_count: int,
        paragraphs: list[Paragraph],
        characters: list[Character],
    ) -> list[dict[str, Any]]:
        if not isinstance(raw_scenes, list):
            return []

        valid_paragraph_ids = {paragraph.id for paragraph in paragraphs}
        normalized: list[dict[str, Any]] = []
        for index, item in enumerate(raw_scenes[:scene_count], start=1):
            if not isinstance(item, dict):
                continue

            source_ids = [
                paragraph_id
                for paragraph_id in self._ensure_int_list(item.get("source_paragraphs"))
                if paragraph_id in valid_paragraph_ids
            ]
            if not source_ids:
                source_ids = self._paragraph_ids_for_index(index, scene_count, paragraphs)

            scene_characters = self._ensure_string_list(item.get("characters"))
            if not scene_characters:
                scene_characters = self._infer_characters(source_ids, paragraphs, characters)

            normalized.append(
                {
                    "scene_id": index,
                    "title": self._clean_text(item.get("title")) or self._fallback_title(index, source_ids, paragraphs),
                    "time": self._clean_text(item.get("time")) or self._infer_time(source_ids, paragraphs),
                    "location": self._clean_text(item.get("location")) or self._infer_location(source_ids, paragraphs),
                    "characters": scene_characters,
                    "plot_goal": self._clean_text(item.get("plot_goal")) or "推进主要人物目标",
                    "conflict": self._clean_text(item.get("conflict")) or "人物在目标、信息或行动上出现阻力",
                    "source_paragraphs": source_ids,
                }
            )

        return normalized

    def _fallback_plan(
        self,
        scene_count: int,
        paragraphs: list[Paragraph],
        characters: list[Character],
    ) -> list[dict[str, Any]]:
        count = min(scene_count, max(1, len(paragraphs)))
        scenes: list[dict[str, Any]] = []
        for index in range(1, count + 1):
            source_ids = self._paragraph_ids_for_index(index, count, paragraphs)
            source_text = self._source_text(source_ids, paragraphs)
            scenes.append(
                {
                    "scene_id": index,
                    "title": self._fallback_title(index, source_ids, paragraphs),
                    "time": self._infer_time(source_ids, paragraphs),
                    "location": self._infer_location(source_ids, paragraphs),
                    "characters": self._infer_characters(source_ids, paragraphs, characters),
                    "plot_goal": self._compact(source_text, 60) or "推进剧情",
                    "conflict": self._infer_conflict(source_text),
                    "source_paragraphs": source_ids,
                }
            )
        return scenes

    def _paragraph_ids_for_index(self, index: int, count: int, paragraphs: list[Paragraph]) -> list[int]:
        start = round((index - 1) * len(paragraphs) / count)
        end = round(index * len(paragraphs) / count)
        selected = paragraphs[start:end] or [paragraphs[min(start, len(paragraphs) - 1)]]
        return [paragraph.id for paragraph in selected]

    def _fallback_title(self, index: int, source_ids: list[int], paragraphs: list[Paragraph]) -> str:
        text = self._source_text(source_ids, paragraphs)
        location = self._infer_location(source_ids, paragraphs)
        event = self._compact(re.sub(r"[，。！？；：、“”\"'（）()]", " ", text).strip(), 12)
        if location != "未知":
            return f"{location}事件"
        return f"关键事件 {index}" if not event else event

    def _infer_time(self, source_ids: list[int], paragraphs: list[Paragraph]) -> str:
        text = self._source_text(source_ids, paragraphs)
        for candidate in ["凌晨", "清晨", "早晨", "上午", "中午", "下午", "傍晚", "黄昏", "夜晚", "深夜", "雨夜"]:
            if candidate in text:
                return candidate
        return "未知"

    def _infer_location(self, source_ids: list[int], paragraphs: list[Paragraph]) -> str:
        text = self._source_text(source_ids, paragraphs)
        location_keywords = [
            "码头",
            "灯塔",
            "出租屋",
            "仓库",
            "医院",
            "学校",
            "办公室",
            "街",
            "巷",
            "车站",
            "客厅",
            "房间",
            "门口",
            "海边",
        ]
        for keyword in location_keywords:
            if keyword in text:
                return keyword

        match = re.search(r"在([^，。！？；]{1,12})(?:里|中|上|下|前|后|门口|附近)", text)
        if match:
            return match.group(1)
        return "未知"

    def _infer_characters(
        self,
        source_ids: list[int],
        paragraphs: list[Paragraph],
        characters: list[Character],
    ) -> list[str]:
        text = self._source_text(source_ids, paragraphs)
        names = [character.name for character in characters if character.name and character.name in text]
        if names:
            return names

        candidates = re.findall(r"[\u4e00-\u9fa5]{2,4}", text)
        stop_words = {"第一章", "第二章", "第三章", "第四章", "一个", "他们", "自己", "父亲", "小说"}
        inferred = []
        for candidate in candidates:
            if candidate in stop_words:
                continue
            if candidate not in inferred:
                inferred.append(candidate)
            if len(inferred) >= 3:
                break
        return inferred or ["未知"]

    def _infer_conflict(self, text: str) -> str:
        if any(keyword in text for keyword in ["不愿", "拒绝", "争", "吵", "威胁", "危险", "失踪", "秘密", "暗号", "追"]):
            return self._compact(text, 48)
        return "角色需要在信息不足的情况下继续行动"

    def _source_text(self, source_ids: list[int], paragraphs: list[Paragraph]) -> str:
        id_set = set(source_ids)
        return "\n".join(paragraph.content for paragraph in paragraphs if paragraph.id in id_set)

    def _clean_text(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def _ensure_string_list(self, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if value:
            return [str(value).strip()]
        return []

    def _ensure_int_list(self, value: Any) -> list[int]:
        if not isinstance(value, list):
            return []

        numbers: list[int] = []
        for item in value:
            text = str(item)
            match = re.search(r"\d+", text)
            if match:
                numbers.append(int(match.group(0)))
        return numbers

    def _compact(self, text: str, limit: int) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        return cleaned[:limit]

    def _loads(self, value: str, default: list) -> list:
        try:
            loaded = json.loads(value)
            return loaded if isinstance(loaded, list) else default
        except json.JSONDecodeError:
            return default
