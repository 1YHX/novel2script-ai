import json
import re
from typing import Any

from models.character import Character
from models.scene import Scene
from models.script import Script


class ConsistencyService:
    def check(
        self,
        characters: list[Character],
        scenes: list[Scene],
        scripts: list[Script],
    ) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        known_names = {character.name for character in characters if character.name}
        latest_scripts = self._latest_scripts_by_scene(scripts)

        for scene in scenes:
            script = latest_scripts.get(scene.id)
            scene_characters = self._loads(scene.characters_json, [])

            if not script:
                issues.append(
                    self._issue(
                        "low",
                        "剧本缺失",
                        scene.scene_index,
                        f"第 {scene.scene_index} 场《{scene.title}》还没有生成单场剧本。",
                        "建议先生成该场剧本，再运行完整一致性检查。",
                    )
                )
                continue

            content = script.content
            issues.extend(self._check_scene_metadata(scene, content))
            issues.extend(self._check_scene_characters(scene, scene_characters, known_names, content))
            issues.extend(self._check_dialog_speakers(scene, known_names, content))

        return self._dedupe(issues)

    def _check_scene_metadata(self, scene: Scene, content: str) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        if scene.location and scene.location != "未知" and scene.location not in content:
            issues.append(
                self._issue(
                    "medium",
                    "地点缺失",
                    scene.scene_index,
                    f"分场地点是“{scene.location}”，但剧本正文没有明确写出该地点。",
                    "建议在场头或动作描写中补充场景地点，保持分场和剧本一致。",
                )
            )

        if scene.time and scene.time != "未知" and scene.time not in content:
            issues.append(
                self._issue(
                    "low",
                    "时间缺失",
                    scene.scene_index,
                    f"分场时间是“{scene.time}”，但剧本正文没有明确写出该时间。",
                    "建议在场头中写明时间，例如“时间：白天”。",
                )
            )

        return issues

    def _check_scene_characters(
        self,
        scene: Scene,
        scene_characters: list[str],
        known_names: set[str],
        content: str,
    ) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        expected_names = [name for name in scene_characters if name and name != "未知"]
        missing_names = [name for name in expected_names if name not in content]
        if missing_names:
            issues.append(
                self._issue(
                    "high",
                    "出场人物缺失",
                    scene.scene_index,
                    f"分场人物包含“{'、'.join(missing_names)}”，但剧本正文没有出现这些人物。",
                    "建议补充这些人物的动作或对白；如果他们不应出场，则回到分场大纲修改人物列表。",
                )
            )

        declared_names = self._extract_declared_characters(content)
        speakers = self._extract_speakers(content)
        appeared_names = declared_names | speakers
        unexpected_names = sorted(name for name in known_names if name in appeared_names and name not in expected_names)
        if unexpected_names:
            issues.append(
                self._issue(
                    "medium",
                    "额外人物出现",
                    scene.scene_index,
                    f"剧本正文出现“{'、'.join(unexpected_names)}”，但分场人物列表中没有这些人物。",
                    "建议确认这些人物是否应该出场；如应出场，请同步更新分场大纲。",
                )
            )

        return issues

    def _check_dialog_speakers(self, scene: Scene, known_names: set[str], content: str) -> list[dict[str, Any]]:
        speakers = self._extract_speakers(content)
        unknown_speakers = sorted(speaker for speaker in speakers if speaker not in known_names)
        if not unknown_speakers:
            return []

        return [
            self._issue(
                "medium",
                "对白人物未建档",
                scene.scene_index,
                f"剧本对白中出现“{'、'.join(unknown_speakers)}”，但人物档案中没有对应角色。",
                "建议补充人物档案，或统一对白说话人的名称。",
            )
        ]

    def _extract_speakers(self, content: str) -> set[str]:
        speakers: set[str] = set()
        for line in content.splitlines():
            stripped = line.strip().strip("*").strip()
            match = re.match(r"^([\u4e00-\u9fa5A-Za-z0-9·]{2,12})[:：]$", stripped)
            if match:
                speakers.add(match.group(1))
        return speakers

    def _extract_declared_characters(self, content: str) -> set[str]:
        declared: set[str] = set()
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped.startswith("人物"):
                continue
            _, _, names_text = stripped.partition("：")
            if not names_text:
                _, _, names_text = stripped.partition(":")
            for name in re.split(r"[、,，/ ]+", names_text):
                cleaned = name.strip()
                if cleaned:
                    declared.add(cleaned)
        return declared

    def _latest_scripts_by_scene(self, scripts: list[Script]) -> dict[int, Script]:
        latest: dict[int, Script] = {}
        for script in scripts:
            current = latest.get(script.scene_id)
            if current is None or script.version > current.version:
                latest[script.scene_id] = script
        return latest

    def _issue(self, level: str, issue_type: str, scene_id: int, description: str, suggestion: str) -> dict[str, Any]:
        return {
            "level": level,
            "type": issue_type,
            "scene_id": scene_id,
            "description": description,
            "suggestion": suggestion,
        }

    def _dedupe(self, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen = set()
        deduped = []
        for issue in issues:
            key = (issue["level"], issue["type"], issue["scene_id"], issue["description"])
            if key in seen:
                continue
            seen.add(key)
            deduped.append(issue)
        return deduped

    def _loads(self, value: str, default: list) -> list:
        try:
            loaded = json.loads(value)
            return loaded if isinstance(loaded, list) else default
        except json.JSONDecodeError:
            return default
