# Novel2Script AI

结构化小说转剧本工作台。

## 演示视频

[Bilibili 演示视频](https://www.bilibili.com/video/BV15AEt6SEiY/?spm_id_from=333.1007.top_right_bar_window_history.content.click&vd_source=7647988dfa6fcd4a1c6f6042248bd18f)

## 项目简介

本项目面向网文、短剧和影视剧本创作场景，将小说文本拆解为人物、事件、场景和对白结构，并通过可编辑的分场工作流生成规范剧本。
导入文本会进行基础质量校验：解析结果必须包含至少 3 个章节，保证后续改编流程有足够上下文。

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

## YAML Schema 设计原因

YAML 是本项目的核心结构化导出格式。项目没有把 AI 输出保存成一整段不可解析的文本，而是把小说改编过程拆成可编辑、可追溯、可继续生成的结构：

```yaml
schema_version: "1.0"
project: {}
source: {}
story_skeleton: {}
adaptation_strategy: {}
characters: []
scenes: []
```

这样设计主要有 6 个原因：

1. 分层表达改编过程  
   小说不能稳定地一步变成完整剧本。Schema 将结果拆成 `story_skeleton`、`adaptation_strategy`、`characters`、`scenes`、`beat` 和 `script`，分别对应故事结构、改编决策、人物档案、分场大纲、场景节拍和剧本文本。

2. 保留故事规划依据  
   `story_skeleton.content` 保存故事核、人物弧线、三幕结构和关键转折，避免后续分场只按段落硬切。

3. 保留改编取舍依据  
   `adaptation_strategy.content` 保存主线保留、删减原则、世界观呈现和情绪节奏，让剧本生成有明确约束。

4. 支持原文追溯  
   `characters[].evidence` 和 `scenes[].source_paragraphs` 记录人物与场景来自哪里，作者可以回到原文校对，减少 AI 编造和人物失真。

5. 支持作者继续编辑  
   `script.content` 使用纯文本块，作者可以直接修改；`script.version` 记录剧本版本，方便后续继续打磨。

6. 支持后续自动化处理  
   `time`、`location`、`characters`、`beat.plot_goal`、`beat.conflict` 都是结构化字段，后续可以继续用于剧本编辑、格式转换、分场检查或二次生成。

完整字段定义见 `docs/yaml_schema.md`。

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
