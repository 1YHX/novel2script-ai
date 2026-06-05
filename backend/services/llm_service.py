import json
import re
from typing import Any, Optional

import httpx

from config import get_settings


class LLMError(RuntimeError):
    pass


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        if self.settings.use_mock_llm:
            return self._mock_chat(system_prompt, user_prompt)
        if not self.settings.llm_api_key:
            raise LLMError("未配置 LLM_API_KEY，请设置 USE_MOCK_LLM=true 或配置真实模型 API Key")

        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.4,
        }
        headers = {"Authorization": f"Bearer {self.settings.llm_api_key}", "Content-Type": "application/json"}

        try:
            with httpx.Client(timeout=60) as client:
                response = client.post(f"{self.settings.llm_base_url.rstrip('/')}/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise LLMError(f"模型接口调用失败：{exc}") from exc

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("模型接口响应格式异常") from exc

    def generate_json(self, system_prompt: str, user_prompt: str, schema_name: str) -> dict:
        if self.settings.use_mock_llm:
            return self._mock_json(schema_name)

        raw_output = self.chat(system_prompt, user_prompt)
        return self._parse_json(raw_output, schema_name)

    def _parse_json(self, raw_output: str, schema_name: str) -> dict[str, Any]:
        candidates = [raw_output.strip()]
        extracted = self._extract_json(raw_output)
        if extracted:
            candidates.append(extracted)

        for candidate in candidates:
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

        raise LLMError(f"{schema_name} 输出不是合法 JSON，请检查模型返回内容")

    def _extract_json(self, raw_output: str) -> Optional[str]:
        fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_output, re.DOTALL)
        if fenced_match:
            return fenced_match.group(1)

        start = raw_output.find("{")
        end = raw_output.rfind("}")
        if start != -1 and end != -1 and end > start:
            return raw_output[start : end + 1]

        return None

    def _mock_chat(self, system_prompt: str, user_prompt: str) -> str:
        if "剧本创作" in system_prompt:
            return (
                "第 1 场 深夜来电\n\n"
                "时间：夜晚\n"
                "地点：林川的出租屋\n"
                "人物：林川、苏晚\n\n"
                "【内景，出租屋，夜】\n\n"
                "窗外雨声不断。林川坐在电脑前，屏幕上停留着父亲失踪前的最后一封邮件。\n\n"
                "手机响起。\n\n"
                "林川：\n谁？\n\n"
                "苏晚：\n你父亲不是失踪，他是在躲人。"
            )
        return "这是 Mock LLM 响应。"

    def _mock_json(self, schema_name: str) -> dict[str, Any]:
        mock_map = {
            "characters": {
                "characters": [
                    {
                        "name": "林川",
                        "role": "男主",
                        "personality": ["冷静", "内敛", "执着"],
                        "goal": "查清父亲失踪真相",
                        "first_appearance": "第一章 雨夜",
                        "relations": [{"target": "苏晚", "relation": "合作调查"}],
                        "evidence": "林川反复查看父亲失踪前留下的最后一封邮件。",
                    },
                    {
                        "name": "苏晚",
                        "role": "线索提供者",
                        "personality": ["谨慎", "果断"],
                        "goal": "帮助林川找到旧仓库线索",
                        "first_appearance": "第一章 雨夜",
                        "relations": [{"target": "林川", "relation": "合作调查"}],
                        "evidence": "苏晚在电话中提醒林川：你父亲不是失踪，他是在躲人。",
                    },
                ]
            },
            "scenes": {
                "scenes": [
                    {
                        "scene_id": 1,
                        "title": "深夜来电",
                        "time": "夜晚",
                        "location": "林川的出租屋",
                        "characters": ["林川", "苏晚"],
                        "plot_goal": "引出父亲失踪背后的疑点",
                        "conflict": "林川无法判断苏晚线索的真伪",
                        "source_paragraphs": [1, 2, 3],
                    },
                    {
                        "scene_id": 2,
                        "title": "旧仓库疑云",
                        "time": "深夜",
                        "location": "城西旧仓库",
                        "characters": ["林川", "苏晚", "戴帽子的男人"],
                        "plot_goal": "让林川发现父亲留下的怀表",
                        "conflict": "神秘人暗示苏晚不可信",
                        "source_paragraphs": [4, 5, 6],
                    },
                ]
            },
            "consistency": {
                "issues": [
                    {
                        "level": "medium",
                        "type": "剧情转场不足",
                        "scene_id": 2,
                        "description": "角色从出租屋到旧仓库的过程较快，缺少到达原因和路途压力。",
                        "suggestion": "建议补充一段转场描写，强化林川赶往旧仓库的动机。",
                    }
                ]
            },
        }
        return mock_map.get(schema_name, {})
