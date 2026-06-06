import json
from typing import Optional

from models.character import Character
from models.scene import Scene
from models.script import Script


class ExportService:
    def build_yaml(
        self,
        title: str,
        novel_id: int,
        chapter_count: int,
        strategy: str,
        characters: list[Character],
        scenes: list[Scene],
        scripts: list[Script],
    ) -> str:
        script_by_scene_id = {script.scene_id: script for script in scripts}

        data = {
            "schema_version": "1.0",
            "project": {
                "id": novel_id,
                "title": title,
                "type": "novel_to_script",
                "language": "zh-CN",
            },
            "source": {
                "kind": "novel",
                "minimum_chapters_required": 3,
                "chapter_count": chapter_count,
                "meets_requirement": chapter_count >= 3,
            },
            "adaptation_strategy": {
                "content": strategy,
            },
            "characters": [self._character_to_dict(character) for character in characters],
            "scenes": [self._scene_to_dict(scene, script_by_scene_id.get(scene.id)) for scene in scenes],
        }
        return self._dump_yaml(data)

    def build_markdown(
        self,
        title: str,
        strategy: str,
        characters: list[Character],
        scenes: list[Scene],
        scripts: list[Script],
    ) -> str:
        script_by_scene_id = {script.scene_id: script for script in scripts}

        lines = [
            "# 小说剧本改编结果",
            "",
            f"项目：{title}",
            "",
            "## 一、改编策略",
            "",
            strategy or "暂无改编策略。",
            "",
            "## 二、人物档案",
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

        lines.extend(["## 三、分场大纲", ""])
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

        lines.extend(["## 四、完整剧本", ""])
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

        return "\n".join(lines)

    def _character_to_dict(self, character: Character) -> dict:
        return {
            "id": character.id,
            "name": character.name,
            "role": character.role,
            "personality": self._loads(character.personality_json, []),
            "goal": character.goal,
            "first_appearance": character.first_appearance,
            "relations": self._loads(character.relations_json, []),
            "evidence": character.evidence,
        }

    def _scene_to_dict(self, scene: Scene, script: Optional[Script]) -> dict:
        return {
            "scene_id": scene.scene_index,
            "title": scene.title,
            "time": scene.time,
            "location": scene.location,
            "characters": self._loads(scene.characters_json, []),
            "beat": {
                "plot_goal": scene.plot_goal,
                "conflict": scene.conflict,
            },
            "source_paragraphs": self._loads(scene.source_paragraphs_json, []),
            "script": {
                "version": script.version if script else None,
                "format": "plain_text",
                "content": script.content if script else "",
            },
        }

    def _dump_yaml(self, value, indent: int = 0) -> str:
        lines = self._yaml_lines(value, indent)
        return "\n".join(lines) + "\n"

    def _yaml_lines(self, value, indent: int) -> list[str]:
        spaces = " " * indent
        if isinstance(value, dict):
            lines: list[str] = []
            for key, item in value.items():
                if isinstance(item, (dict, list)):
                    lines.append(f"{spaces}{key}:")
                    lines.extend(self._yaml_lines(item, indent + 2))
                elif isinstance(item, str) and "\n" in item:
                    lines.append(f"{spaces}{key}: |-")
                    lines.extend(f"{' ' * (indent + 2)}{line}" for line in item.splitlines())
                else:
                    lines.append(f"{spaces}{key}: {self._yaml_scalar(item)}")
            return lines
        if isinstance(value, list):
            if not value:
                return [f"{spaces}[]"]
            lines = []
            for item in value:
                if isinstance(item, dict):
                    lines.append(f"{spaces}-")
                    lines.extend(self._yaml_lines(item, indent + 2))
                elif isinstance(item, list):
                    lines.append(f"{spaces}-")
                    lines.extend(self._yaml_lines(item, indent + 2))
                else:
                    lines.append(f"{spaces}- {self._yaml_scalar(item)}")
            return lines
        return [f"{spaces}{self._yaml_scalar(value)}"]

    def _yaml_scalar(self, value) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)

        text = str(value)
        return json.dumps(text, ensure_ascii=False)

    def _loads(self, value: str, default: list) -> list:
        try:
            loaded = json.loads(value)
            return loaded if isinstance(loaded, list) else default
        except json.JSONDecodeError:
            return default
