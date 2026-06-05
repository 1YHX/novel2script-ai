import json
from typing import Optional

from models.character import Character
from models.scene import Scene
from models.script import Script


class ExportService:
    def build_markdown(
        self,
        title: str,
        characters: list[Character],
        scenes: list[Scene],
        scripts: list[Script],
        issues: Optional[list[dict]] = None,
    ) -> str:
        issue_items = issues or []
        script_by_scene_id = {script.scene_id: script for script in scripts}

        lines = [
            "# 小说剧本改编结果",
            "",
            f"项目：{title}",
            "",
            "## 一、人物档案",
            "",
        ]

        if characters:
            for character in characters:
                personality = "、".join(self._loads(character.personality_json, []))
                relations = self._loads(character.relations_json, [])
                relation_text = "；".join(
                    f"{item.get('target', '未知')} / {item.get('relation', '未知')}"
                    for item in relations
                    if isinstance(item, dict)
                )
                lines.extend(
                    [
                        f"### {character.name}",
                        "",
                        f"- 身份：{character.role}",
                        f"- 性格：{personality or '未知'}",
                        f"- 目标：{character.goal}",
                        f"- 首次出现：{character.first_appearance}",
                        f"- 关系：{relation_text or '未知'}",
                        f"- 证据：{character.evidence or '无'}",
                        "",
                    ]
                )
        else:
            lines.extend(["暂无人物档案。", ""])

        lines.extend(["## 二、分场大纲", ""])
        if scenes:
            for scene in scenes:
                characters_text = "、".join(self._loads(scene.characters_json, []))
                paragraph_text = "、".join(str(item) for item in self._loads(scene.source_paragraphs_json, []))
                lines.extend(
                    [
                        f"### 第 {scene.scene_index} 场：{scene.title}",
                        "",
                        f"- 时间：{scene.time}",
                        f"- 地点：{scene.location}",
                        f"- 人物：{characters_text or '未知'}",
                        f"- 剧情目的：{scene.plot_goal}",
                        f"- 冲突点：{scene.conflict}",
                        f"- 对应小说段落：{paragraph_text or '未知'}",
                        "",
                    ]
                )
        else:
            lines.extend(["暂无分场大纲。", ""])

        lines.extend(["## 三、完整剧本", ""])
        if scenes:
            for scene in scenes:
                script = script_by_scene_id.get(scene.id)
                lines.extend([f"### 第 {scene.scene_index} 场：{scene.title}", ""])
                if script:
                    lines.extend([script.content, ""])
                else:
                    lines.extend(["该场景尚未生成剧本。", ""])
        else:
            lines.extend(["暂无剧本内容。", ""])

        lines.extend(["## 四、一致性检查报告", ""])
        if issue_items:
            for issue in issue_items:
                lines.extend(
                    [
                        f"### {issue.get('type', '未知问题')}",
                        "",
                        f"- 等级：{issue.get('level', 'unknown')}",
                        f"- 场景：{issue.get('scene_id', '未知')}",
                        f"- 描述：{issue.get('description', '')}",
                        f"- 建议：{issue.get('suggestion', '')}",
                        "",
                    ]
                )
        else:
            lines.extend(["暂无一致性检查报告。", ""])

        return "\n".join(lines)

    def _loads(self, value: str, default: list) -> list:
        try:
            loaded = json.loads(value)
            return loaded if isinstance(loaded, list) else default
        except json.JSONDecodeError:
            return default
