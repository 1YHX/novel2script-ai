# Novel2Script AI

结构化小说转剧本工作台。

## 项目简介

本项目面向网文、短剧和影视剧本创作场景，将小说文本拆解为人物、事件、场景和对白结构，并通过可编辑的分场工作流生成规范剧本。

## 项目亮点

1. 多阶段小说改编流程
2. 结构化 Schema 约束
3. 人物一致性维护
4. 分场式剧本生成
5. 可解释的检查报告

## 技术架构

- 前端：Vue 3 + Vite + Element Plus + Axios
- 后端：FastAPI + SQLite + SQLModel
- AI：统一 LLMService 封装，支持 Mock 模式

## 快速启动

### 后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 环境变量配置

```bash
USE_MOCK_LLM=true
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

## 项目结构

项目按照 `TASK.md` 要求拆分为 `backend/`、`frontend/`、`examples/` 和 `docs/`。

## 核心功能

- 小说导入与解析
- 人物档案抽取
- 分场大纲生成
- 单场剧本生成与编辑
- 一致性检查
- Markdown 导出

## API 接口

当前已实现：

- `GET /api/health`

## 示例数据

示例小说位于 `examples/demo_novel.txt`。

## Demo 视频

待补充。

## 开发过程与 PR 记录

- PR 1：初始化项目结构与前后端基础环境

## 未来规划

- 人物关系图
- 多风格剧本生成
- 剧本版本对比
