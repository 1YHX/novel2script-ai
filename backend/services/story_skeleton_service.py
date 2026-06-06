import json
import re
from pathlib import Path
from typing import Optional

from models.character import Character
from models.chapter import Chapter
from models.novel import Novel
from services.llm_service import LLMError, LLMService


class StorySkeletonService:
    def __init__(self, llm_service: Optional[LLMService] = None) -> None:
        self.llm_service = llm_service or LLMService()

    def generate(self, novel: Novel, chapters: list[Chapter], characters: list[Character]) -> str:
        system_prompt = (Path(__file__).resolve().parents[1] / "prompts" / "story_skeleton.txt").read_text(
            encoding="utf-8"
        )
        user_prompt = self._build_user_prompt(novel, chapters, characters)
        try:
            return self.llm_service.chat(system_prompt, user_prompt).strip()
        except LLMError:
            return self._fallback_skeleton(novel, chapters, characters)

    def _build_user_prompt(self, novel: Novel, chapters: list[Chapter], characters: list[Character]) -> str:
        character_lines = []
        for character in characters:
            personality = "、".join(self._loads(character.personality_json, []))
            character_lines.append(f"- {character.name}：{character.role}；性格：{personality}；目标：{character.goal}")

        event_lines = ["| 章节 | 涉及角色 | 核心事件 | 主线关系 | 信息密度 | 情绪 |", "|---|---|---|---|---|---|"]
        for chapter in chapters[:100]:
            text = self._compact(chapter.content, 360)
            involved = [character.name for character in characters if character.name and character.name in text]
            event_lines.append(
                "| {chapter} | {roles} | {event} | {mainline} | {density} | {emotion} |".format(
                    chapter=f"第{chapter.order_index}章 {chapter.title}",
                    roles="、".join(involved[:5]) or "未知",
                    event=self._compact(text, 80),
                    mainline=self._mainline_weight(text),
                    density=self._density(text),
                    emotion=self._emotion(text),
                )
            )

        return "\n\n".join(
            [
                f"小说标题：{novel.title}",
                f"章节数量：{len(chapters)}",
                "人物档案：\n" + ("\n".join(character_lines) if character_lines else "暂无人物档案"),
                "章节事件表：\n" + "\n".join(event_lines),
                "请输出故事骨架。",
            ]
        )

    def _fallback_skeleton(self, novel: Novel, chapters: list[Chapter], characters: list[Character]) -> str:
        main_character = characters[0].name if characters else "主角"
        first = chapters[0].order_index if chapters else 1
        last = chapters[-1].order_index if chapters else 1
        mid = first + max(0, (last - first) // 2)
        return "\n".join(
            [
                "# 故事骨架",
                "",
                "## 故事核",
                f"- 一句话：{main_character}在连续危机中追索目标，并在关键真相中完成选择。",
                "- 吸引力：保留目标、危机、真相和关系变化，把静态叙述转成可拍摄冲突。",
                "",
                "## 主角弧线",
                f"- 初始状态：{main_character}处在信息不足或目标受阻的状态。",
                "- 关键变故：核心秘密、危机或关系冲突逼迫角色行动。",
                "- 行动目标：解决眼前阻力，同时逼近更大的真相。",
                "- 最终变化：从被动应对转向主动选择。",
                "",
                "## 三幕结构",
                "### 第一幕：建立与触发",
                f"- 覆盖章节：第{first}-{mid}章前段",
                "- 核心问题：主角为什么必须行动？",
                "- 关键转折：出现不可回避的危机或线索。",
                "- 情绪任务：快速建立人物目标和主要矛盾。",
                "",
                "### 第二幕：对抗与升级",
                f"- 覆盖章节：第{mid}章附近",
                "- 核心问题：主角如何在阻力中推进目标？",
                "- 关键转折：敌对力量或误会升级。",
                "- 情绪任务：强化冲突、悬念和关系拉扯。",
                "",
                "### 第三幕：高潮与收束",
                f"- 覆盖章节：第{mid + 1}-{last}章",
                "- 核心问题：主角如何完成最终选择？",
                "- 关键转折：核心真相或最终对抗出现。",
                "- 情绪任务：释放前期铺垫，形成可继续打磨的结尾。",
                "",
                "## 删减与合并原则",
                "- 保留：人物目标变化、危机场面、真相线索和关系转折。",
                "- 压缩：重复解释、过渡日常和弱动作段落。",
                "- 删除：不影响主线、不改变人物关系的旁支内容。",
            ]
        )

    def _mainline_weight(self, text: str) -> str:
        if any(keyword in text for keyword in ["目标", "秘密", "真相", "危险", "死亡", "威胁", "身份", "系统", "任务"]):
            return "强"
        if any(keyword in text for keyword in ["回忆", "关系", "解释", "线索", "准备"]):
            return "中"
        return "弱"

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
            ("悬疑", ["秘密", "真相", "线索", "谜"]),
            ("危险", ["死", "枪", "逃", "危险", "杀"]),
            ("转折", ["突然", "却", "但是", "没想到"]),
            ("情感", ["哭", "爱", "母亲", "父亲", "痛苦"]),
        ]:
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
        return "+".join(tags[:3]) or "平铺"

    def _compact(self, text: str, limit: int) -> str:
        return re.sub(r"\s+", " ", text or "").strip()[:limit]

    def _loads(self, value: str, default: list) -> list:
        try:
            loaded = json.loads(value)
            return loaded if isinstance(loaded, list) else default
        except json.JSONDecodeError:
            return default
