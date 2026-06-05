# 架构说明

Novel2Script AI 采用前后端分离架构。

- 前端：Vue 3、Vite、Element Plus、Axios
- 后端：FastAPI、SQLModel、SQLite
- AI：通过统一的 `LLMService` 封装，后续支持真实模型与 Mock 模式切换

核心流程为：小说导入、文本解析、人物抽取、分场大纲、单场剧本、编辑保存和结构化导出。
