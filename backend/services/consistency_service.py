import json
import re
from difflib import SequenceMatcher
from typing import Any, Optional

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
        alias_issues: list[dict[str, Any]] = []
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
            scene_issues, scene_alias_issues = self._check_scene_characters(
                scene, scene_characters, known_names, content
            )
            issues.extend(scene_issues)
            alias_issues.extend(scene_alias_issues)
            speaker_issues, speaker_alias_issues = self._check_dialog_speakers(scene, known_names, content)
            issues.extend(speaker_issues)
            alias_issues.extend(speaker_alias_issues)

        return self._dedupe(alias_issues + issues)

    def _check_scene_metadata(self, scene: Scene, content: str) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        declared_location = self._extract_field_value(content, "地点")
        expected_location = self._normalize_location(scene.location)
        actual_location = self._normalize_location(declared_location or content)
        if expected_location and expected_location not in actual_location:
            issues.append(
                self._issue(
                    "medium",
                    "地点缺失",
                    scene.scene_index,
                    f"分场地点是“{scene.location}”，但剧本场头没有明确写出该地点。",
                    "建议在剧本场头补充或统一地点名称，保持分场和剧本一致。",
                )
            )

        declared_time = self._extract_field_value(content, "时间")
        expected_time = self._normalize_time(scene.time)
        actual_time = self._normalize_time(declared_time)
        if expected_time and expected_time not in actual_time:
            issues.append(
                self._issue(
                    "low",
                    "时间缺失",
                    scene.scene_index,
                    f"分场时间是“{scene.time}”，但剧本场头没有明确写出该时间。",
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
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        issues: list[dict[str, Any]] = []
        alias_issues: list[dict[str, Any]] = []
        expected_names = [name for name in scene_characters if name and name != "未知"]
        missing_names = []
        for name in expected_names:
            if name in content:
                continue
            alias = self._find_similar_name(name, known_names)
            if alias and alias in content:
                alias_issues.append(self._name_alias_issue(scene.scene_index, name, alias))
                continue
            missing_names.append(name)
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
        unexpected_names = []
        for name in sorted(appeared_names):
            if self._name_in_set(name, set(expected_names)):
                continue
            alias = self._find_similar_name(name, known_names)
            if alias:
                alias_issues.append(self._name_alias_issue(scene.scene_index, name, alias))
                continue
            if name in known_names:
                unexpected_names.append(name)
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

        return issues, alias_issues

    def _check_dialog_speakers(
        self, scene: Scene, known_names: set[str], content: str
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        speakers = self._extract_speakers(content)
        unknown_speakers = []
        alias_issues = []
        for speaker in sorted(speakers):
            if self._name_in_set(speaker, known_names):
                continue
            alias = self._find_similar_name(speaker, known_names)
            if alias:
                alias_issues.append(self._name_alias_issue(scene.scene_index, speaker, alias))
            else:
                unknown_speakers.append(speaker)
        if not unknown_speakers:
            return [], alias_issues

        return [
            self._issue(
                "medium",
                "对白人物未建档",
                scene.scene_index,
                f"剧本对白中出现“{'、'.join(unknown_speakers)}”，但人物档案中没有对应角色。",
                "建议补充人物档案，或统一对白说话人的名称。",
            )
        ], alias_issues

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

    def _extract_field_value(self, content: str, field_name: str) -> str:
        pattern = re.compile(rf"^\s*{field_name}\s*[:：]\s*(.+?)\s*$")
        for line in content.splitlines()[:20]:
            match = pattern.match(line.strip())
            if match:
                return match.group(1)
        return ""

    def _normalize_location(self, value: str) -> str:
        text = re.sub(r"\s+", "", value or "")
        text = re.sub(r"[（）()《》「」『』]", "", text)
        text = re.sub(r"(内部|内|里|中)$", "", text)
        return text if text != "未知" else ""

    def _normalize_time(self, value: str) -> str:
        text = re.sub(r"[（(].*?[）)]", "", value or "")
        text = re.sub(r"\s+", "", text)
        return text if text != "未知" else ""

    def _name_in_set(self, name: str, names: set[str]) -> bool:
        return name in names or any(name == self._clean_name(candidate) for candidate in names)

    def _find_similar_name(self, name: str, names: set[str]) -> Optional[str]:
        for candidate in names:
            if name == candidate:
                return candidate
            cleaned_candidate = self._clean_name(candidate)
            if name == cleaned_candidate:
                continue
            if len(name) >= 2 and len(candidate) >= 2:
                if name in cleaned_candidate or cleaned_candidate in name:
                    return candidate
                if SequenceMatcher(None, name, cleaned_candidate).ratio() >= 0.72:
                    return candidate
        return None

    def _clean_name(self, name: str) -> str:
        return re.sub(r"[（(].*?[）)]", "", name or "").strip()

    def _name_alias_issue(self, scene_id: int, script_name: str, profile_name: str) -> dict[str, Any]:
        return self._issue(
            "low",
            "人物名称不一致",
            scene_id,
            f"剧本或分场中使用“{script_name}”，人物档案中相近名称是“{profile_name}”。",
            "建议统一人物名称，或在人物档案中补充别名说明。",
        )

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
            if issue["type"] == "人物名称不一致":
                key = (issue["level"], issue["type"], issue["description"])
            else:
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
