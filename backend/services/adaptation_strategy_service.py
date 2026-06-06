import json
import re
from pathlib import Path
from typing import Optional

from models.character import Character
from models.chapter import Chapter
from models.novel import Novel
from services.llm_service import LLMError, LLMService


class AdaptationStrategyService:
    def __init__(self, llm_service: Optional[LLMService] = None) -> None:
        self.llm_service = llm_service or LLMService()

    def generate(self, novel: Novel, chapters: list[Chapter], characters: list[Character]) -> str:
        system_prompt = (Path(__file__).resolve().parents[1] / "prompts" / "adaptation_strategy.txt").read_text(
            encoding="utf-8"
        )
        user_prompt = self._build_user_prompt(novel, chapters, characters)
        try:
            return self.llm_service.chat(system_prompt, user_prompt).strip()
        except LLMError:
            return self._fallback_strategy(novel, chapters, characters)

    def _build_user_prompt(self, novel: Novel, chapters: list[Chapter], characters: list[Character]) -> str:
        character_lines = []
        for character in characters:
            personality = "、".join(self._loads(character.personality_json, []))
            character_lines.append(f"- {character.name}：{character.role}；性格：{personality}；目标：{character.goal}")

        event_lines = ["| 章节 | 核心事件 | 信息密度 | 情绪 |", "|---|---|---|---|"]
        for chapter in chapters[:80]:
            text = self._compact(chapter.content, 280)
            event_lines.append(
                f"| 第{chapter.order_index}章 {chapter.title} | {self._compact(text, 70)} | {self._density(text)} | {self._emotion(text)} |"
            )

        return "\n\n".join(
            [
                f"小说标题：{novel.title}",
                "人物档案：\n" + ("\n".join(character_lines) if character_lines else "暂无人物档案"),
                "章节事件表：\n" + "\n".join(event_lines),
                "请输出改编策略。",
            ]
        )

    def _fallback_strategy(self, novel: Novel, chapters: list[Chapter], characters: list[Character]) -> str:
        main_character = characters[0].name if characters else "主角"
        return "\n".join(
            [
                "核心改编原则",
                f"围绕《{novel.title}》的主线推进改编，优先保留{main_character}目标变化、关键冲突和高情绪场面。",
                "",
                "主线保留与删减",
                "保留直接推动目标、身份、危机和关系变化的章节；压缩重复解释、静态心理描写和弱动作段落。",
                "",
                "世界观呈现策略",
                "通过角色行动和台词逐步释放设定，避免长段说明，把复杂背景拆进场景冲突中。",
                "",
                "情绪与节奏策略",
                "每场至少设置一个明确阻力或转折，场尾保留下一步行动钩子，保证剧本初稿可继续打磨。",
            ]
        )

    def _density(self, text: str) -> str:
        if len(text) >= 700:
            return "高"
        if len(text) >= 260:
            return "中"
        return "低"

    def _emotion(self, text: str) -> str:
        tags = []
        for tag, keywords in [
            ("冲突", ["争", "怒", "拒绝", "威胁"]),
            ("悬疑", ["秘密", "真相", "线索"]),
            ("危险", ["死", "枪", "逃", "危险"]),
            ("情感", ["哭", "爱", "母亲", "父亲"]),
        ]:
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
        return "+".join(tags) or "平铺"

    def _compact(self, text: str, limit: int) -> str:
        return re.sub(r"\s+", " ", text or "").strip()[:limit]

    def _loads(self, value: str, default: list) -> list:
        try:
            loaded = json.loads(value)
            return loaded if isinstance(loaded, list) else default
        except json.JSONDecodeError:
            return default
