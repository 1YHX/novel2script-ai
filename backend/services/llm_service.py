class LLMService:
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError("LLMService will be implemented in the LLM service milestone.")

    def generate_json(self, system_prompt: str, user_prompt: str, schema_name: str) -> dict:
        raise NotImplementedError("LLMService will be implemented in the LLM service milestone.")
