# Novel2Script AI

结构化小说转剧本工作台。

## 项目简介

本项目面向网文、短剧和影视剧本创作场景，将小说文本拆解为人物、事件、场景和对白结构，并通过可编辑的分场工作流生成规范剧本。
导入文本会严格校验题目要求：解析结果必须包含至少 3 个章节。

## 项目亮点

1. 多阶段小说改编流程
2. 结构化 Schema 约束
3. 原文段落追溯
4. 分场式剧本生成
5. YAML 与 Markdown 双格式导出

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
cd backend
cp .env.example .env
```

默认使用 DeepSeek 兼容 OpenAI Chat Completions 的接口配置。演示时可保持 Mock 模式：

```bash
USE_MOCK_LLM=true
LLM_API_KEY=
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

接入真实 DeepSeek 时，将 `backend/.env` 改为：

```bash
USE_MOCK_LLM=false
LLM_API_KEY=你的 DeepSeek API Key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

## 项目结构

项目拆分为 `backend/`、`frontend/`、`examples/` 和 `docs/`，前后端职责清晰，便于演示和迭代。

## 核心功能

- 小说导入与解析
- 演示登录与项目记录恢复
- 人物档案抽取
- 故事骨架生成
- 改编策略生成
- 分场大纲生成
- 单场剧本生成与编辑
- YAML 导出
- Markdown 导出

## API 接口

当前已实现：

- `GET /api/health`
- `POST /api/auth/login`
- `GET /api/novels`
- `POST /api/novels/import`
- `POST /api/characters/extract/{novel_id}`
- `GET /api/characters/{novel_id}`
- `POST /api/skeletons/generate/{novel_id}`
- `GET /api/skeletons/{novel_id}`
- `POST /api/strategies/generate/{novel_id}`
- `GET /api/strategies/{novel_id}`
- `POST /api/scenes/plan/{novel_id}`
- `GET /api/scenes/{novel_id}`
- `POST /api/scripts/generate/{scene_id}`
- `GET /api/scripts/{scene_id}`
- `PUT /api/scripts/{script_id}`
- `GET /api/export/markdown/{novel_id}`
- `GET /api/export/yaml/{novel_id}`

## 示例数据

示例小说位于 `examples/demo_novel.txt`。

剧本 YAML Schema 文档位于 `docs/yaml_schema.md`。

## Demo 视频

待补充。

## 开发过程与 PR 记录

- PR 1：初始化项目结构与前后端基础环境
- PR 2：实现小说文本导入与章节段落解析
- PR 3：实现 LLMService 与 Prompt 管理
- PR 4：实现人物档案抽取与角色卡展示
- PR 5：实现分场大纲生成与场景列表展示
- PR 6：实现单场剧本生成与编辑保存
- PR 7：实现 Markdown 导出与示例数据
- PR 8：实现 YAML 导出与 Schema 文档

## 未来规划

- 人物关系图
- 多风格剧本生成
- 剧本版本对比
