# TASK.md — AI 小说转剧本工作台开发任务书

## 0. 项目背景

本项目用于参加「七牛云 × XEngineer 暑期实训」第二批次议题三：**AI 小说转剧本工具**。

评审重点包括：

- 作品完整度与创新性：40%
- 开发过程与质量：40%
- 演示与表达：20%

因此本项目不能做成简单的「把小说文本直接丢给 AI，然后输出剧本」的套壳工具，而应做成一个完整的、可演示的、结构化的 **AI 小说改编工作台**。

核心思想：

> AI 负责生成，系统负责拆解、组织、约束、校验、编辑和导出。

---

## 1. 项目定位

项目名称建议：

- Novel2Script AI
- AI 小说转剧本工作台
- Story2Screen
- 剧本工坊 AI

推荐最终项目名：

> **Novel2Script AI：结构化小说转剧本工作台**

一句话介绍：

> 本项目面向网文、短剧和影视剧本创作场景，将小说文本自动拆解为人物、事件、场景和对白结构，并通过可编辑的分场工作流生成规范剧本，支持人物一致性检查、剧情线追踪和多格式导出。

---

## 2. 核心目标

72 小时内完成一个可运行、可演示、可提交的完整作品。

必须完成的核心闭环：

```text
小说输入/上传
  ↓
章节与段落解析
  ↓
人物档案抽取
  ↓
分场大纲生成
  ↓
单场剧本生成
  ↓
人工编辑与保存
  ↓
一致性检查
  ↓
Markdown / PDF / DOCX 导出
```

---

## 3. 技术栈建议

### 3.1 推荐技术栈

为了 72 小时快速开发，优先选择开发效率高的技术栈。

```text
前端：Vue 3 + Vite + Element Plus + Axios
后端：FastAPI + SQLite + SQLAlchemy / SQLModel
AI 接口：OpenAI / DeepSeek / 通义千问 / 智谱，使用统一 LLMService 封装
导出：Markdown 必做，PDF / DOCX 二选一
```

如果已有 SpringBoot 基础，也可以使用 SpringBoot，但 72 小时内 FastAPI 更快。

### 3.2 运行方式要求

项目必须支持一键启动或清晰启动：

```bash
# backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# frontend
cd frontend
npm install
npm run dev
```

README 必须写清楚：

- 环境要求
- 安装依赖
- 配置 API Key
- 启动前端
- 启动后端
- 示例文本位置
- demo 视频链接

---

## 4. 项目目录结构

请按照以下结构组织代码：

```text
novel2script-ai/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── requirements.txt
│   ├── routers/
│   │   ├── novel.py
│   │   ├── character.py
│   │   ├── scene.py
│   │   ├── script.py
│   │   ├── check.py
│   │   └── export.py
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── parser_service.py
│   │   ├── schema_service.py
│   │   ├── consistency_service.py
│   │   └── export_service.py
│   ├── models/
│   │   ├── novel.py
│   │   ├── character.py
│   │   ├── scene.py
│   │   └── script.py
│   ├── schemas/
│   │   ├── novel.py
│   │   ├── character.py
│   │   ├── scene.py
│   │   ├── script.py
│   │   └── check.py
│   ├── prompts/
│   │   ├── character_extract.txt
│   │   ├── scene_plan.txt
│   │   ├── script_generate.txt
│   │   └── consistency_check.txt
│   └── data/
│       └── novel2script.db
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── api/
│       │   └── index.js
│       ├── pages/
│       │   ├── ImportNovel.vue
│       │   ├── Workspace.vue
│       │   ├── CharacterBoard.vue
│       │   ├── SceneBoard.vue
│       │   ├── ScriptEditor.vue
│       │   └── CheckReport.vue
│       └── components/
│           ├── CharacterCard.vue
│           ├── SceneCard.vue
│           ├── ScriptBlock.vue
│           └── IssueCard.vue
│
├── examples/
│   ├── demo_novel.txt
│   └── output_script.md
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── demo.md
│
├── README.md
└── TASK.md
```

---

## 5. 核心功能模块

## 5.1 小说导入与文本解析

### 功能目标

用户可以粘贴小说文本，或上传 `.txt` 文件。系统自动将文本拆分为章节、段落和基础结构。

### 前端功能

页面：`ImportNovel.vue`

需要包含：

- 文本输入框
- txt 文件上传
- 项目标题输入
- “开始解析”按钮
- 解析进度提示
- 解析结果预览

### 后端接口

```http
POST /api/novels/import
```

请求示例：

```json
{
  "title": "示例小说",
  "content": "第一章 雨夜\n林川接到了一个陌生电话……"
}
```

响应示例：

```json
{
  "novel_id": 1,
  "title": "示例小说",
  "chapter_count": 3,
  "paragraph_count": 24,
  "chapters": [
    {
      "chapter_id": 1,
      "title": "第一章 雨夜",
      "paragraphs": [
        {
          "paragraph_id": 1,
          "content": "林川接到了一个陌生电话……"
        }
      ]
    }
  ]
}
```

### 实现要求

- 使用规则解析章节标题。
- 支持常见章节格式：
  - 第一章
  - 第1章
  - Chapter 1
  - 一、
- 如果没有章节标题，则按段落自动分组。
- 原始文本必须保存到数据库。

---

## 5.2 人物档案抽取

### 功能目标

系统从小说文本中提取人物，并生成结构化人物档案。

### 前端功能

页面：`CharacterBoard.vue`

展示为人物卡片，包括：

- 人物姓名
- 角色定位
- 性格特征
- 人物目标
- 与其他人物的关系
- 首次出现章节
- 相关原文证据

### 后端接口

```http
POST /api/characters/extract/{novel_id}
GET /api/characters/{novel_id}
```

响应示例：

```json
{
  "characters": [
    {
      "id": 1,
      "name": "林川",
      "role": "男主",
      "personality": ["冷静", "内敛", "善于观察"],
      "goal": "查清父亲失踪真相",
      "first_appearance": "第一章 雨夜",
      "relations": [
        {
          "target": "苏晚",
          "relation": "合作伙伴"
        }
      ],
      "evidence": "林川盯着屏幕上的邮件，久久没有说话。"
    }
  ]
}
```

### LLM 输出 Schema

要求大模型严格输出 JSON：

```json
{
  "characters": [
    {
      "name": "string",
      "role": "string",
      "personality": ["string"],
      "goal": "string",
      "first_appearance": "string",
      "relations": [
        {
          "target": "string",
          "relation": "string"
        }
      ],
      "evidence": "string"
    }
  ]
}
```

### 实现要求

- 必须有 prompt 文件：`backend/prompts/character_extract.txt`
- 必须做 JSON 解析失败兜底。
- 如果 AI 输出不是合法 JSON，要进行修复或返回清晰错误。
- 提取结果保存到数据库。

---

## 5.3 分场大纲生成

### 功能目标

系统将小说转化为剧本分场结构，而不是直接生成完整剧本。

这是项目核心亮点之一。

### 前端功能

页面：`SceneBoard.vue`

展示场景卡片：

- 场景编号
- 场景标题
- 时间
- 地点
- 出场人物
- 剧情目的
- 冲突点
- 对应小说段落
- “生成剧本”按钮

### 后端接口

```http
POST /api/scenes/plan/{novel_id}
GET /api/scenes/{novel_id}
```

响应示例：

```json
{
  "scenes": [
    {
      "scene_id": 1,
      "title": "深夜来电",
      "time": "夜晚",
      "location": "林川的出租屋",
      "characters": ["林川", "苏晚"],
      "plot_goal": "引出父亲失踪线索",
      "conflict": "林川不愿相信苏晚提供的信息",
      "source_paragraphs": [1, 2, 3]
    }
  ]
}
```

### LLM 输出 Schema

```json
{
  "scenes": [
    {
      "scene_id": 1,
      "title": "string",
      "time": "string",
      "location": "string",
      "characters": ["string"],
      "plot_goal": "string",
      "conflict": "string",
      "source_paragraphs": [1]
    }
  ]
}
```

### 实现要求

- 必须有 prompt 文件：`backend/prompts/scene_plan.txt`
- 场景数量可由用户选择，默认 5 场。
- 支持“重新生成分场大纲”。
- 分场结果保存到数据库。

---

## 5.4 单场剧本生成与编辑

### 功能目标

用户点击某个场景，系统根据该场景大纲、人物档案和原文片段生成标准剧本。

### 前端功能

页面：`ScriptEditor.vue`

功能包括：

- 选择某一场
- 生成剧本
- 展示剧本内容
- 支持编辑
- 保存修改
- 支持重新生成

### 剧本格式要求

生成内容建议采用以下格式：

```text
第 1 场 深夜来电

时间：夜晚
地点：林川的出租屋
人物：林川、苏晚

【内景，出租屋，夜】

窗外雨声不断。林川坐在电脑前，屏幕上停留着父亲失踪前的最后一封邮件。

手机响起。

林川：
谁？

苏晚：
你父亲不是失踪，他是在躲人。
```

### 后端接口

```http
POST /api/scripts/generate/{scene_id}
GET /api/scripts/{scene_id}
PUT /api/scripts/{script_id}
```

请求示例：

```json
{
  "style": "短剧风格",
  "dialogue_density": "medium",
  "include_camera_language": true
}
```

响应示例：

```json
{
  "script_id": 1,
  "scene_id": 1,
  "content": "第 1 场 深夜来电\n\n时间：夜晚\n地点：林川的出租屋……",
  "version": 1
}
```

### 实现要求

- 必须有 prompt 文件：`backend/prompts/script_generate.txt`
- 生成时必须传入：
  - 场景大纲
  - 人物档案
  - 对应原文段落
  - 用户选择的风格
- 支持编辑后保存。
- 支持版本号递增。

---

## 5.5 一致性检查

### 功能目标

这是项目最重要的创新点之一。系统不能只是生成，还要检查生成结果是否和小说、人物设定、剧情线一致。

### 检查内容

至少检查以下问题：

```text
1. 人物名称是否前后不一致
2. 人物是否出现在不合理的场景中
3. 地点是否前后冲突
4. 时间线是否冲突
5. 角色性格是否突变
6. 对白是否不符合人物设定
7. 剧情是否缺少必要转场
```

### 前端功能

页面：`CheckReport.vue`

展示检查报告：

- 问题等级：high / medium / low
- 问题类型
- 问题描述
- 涉及场景
- 修改建议

### 后端接口

```http
POST /api/check/consistency/{novel_id}
GET /api/check/reports/{novel_id}
```

响应示例：

```json
{
  "issues": [
    {
      "level": "medium",
      "type": "人物名称不一致",
      "scene_id": 3,
      "description": "第 3 场中“苏晚”被称为“小晚”，可能造成人物指代不一致。",
      "suggestion": "建议统一使用“苏晚”，或在前文说明“小晚”是昵称。"
    },
    {
      "level": "high",
      "type": "时间线冲突",
      "scene_id": 5,
      "description": "上一场角色仍在郊区仓库，本场直接出现在医院，缺少转场说明。",
      "suggestion": "建议增加一段转场描写，说明角色如何到达医院。"
    }
  ]
}
```

### LLM 输出 Schema

```json
{
  "issues": [
    {
      "level": "high | medium | low",
      "type": "string",
      "scene_id": 1,
      "description": "string",
      "suggestion": "string"
    }
  ]
}
```

### 实现要求

- 必须有 prompt 文件：`backend/prompts/consistency_check.txt`
- 检查对象包括人物档案、分场大纲和已生成剧本。
- 如果暂时没有问题，也要返回空数组：`{"issues": []}`。
- 报告保存到数据库。

---

## 5.6 导出功能

### 功能目标

支持将生成的剧本导出，方便演示作品完整性。

### 必做

- Markdown 导出

### 选做

- PDF 导出
- DOCX 导出

### 后端接口

```http
GET /api/export/markdown/{novel_id}
GET /api/export/pdf/{novel_id}
GET /api/export/docx/{novel_id}
```

### 导出内容

导出的 Markdown 至少包括：

```markdown
# 小说剧本改编结果

## 一、人物档案

## 二、分场大纲

## 三、完整剧本

## 四、一致性检查报告
```

---

## 6. 数据库设计

使用 SQLite 即可。

### 6.1 novels 表

```text
id
title
content
created_at
updated_at
```

### 6.2 chapters 表

```text
id
novel_id
title
order_index
content
```

### 6.3 paragraphs 表

```text
id
novel_id
chapter_id
order_index
content
```

### 6.4 characters 表

```text
id
novel_id
name
role
personality_json
goal
first_appearance
relations_json
evidence
```

### 6.5 scenes 表

```text
id
novel_id
scene_index
title
time
location
characters_json
plot_goal
conflict
source_paragraphs_json
```

### 6.6 scripts 表

```text
id
novel_id
scene_id
content
version
created_at
updated_at
```

### 6.7 check_reports 表

```text
id
novel_id
issues_json
created_at
```

---

## 7. LLMService 设计

必须封装统一 AI 调用，不要在每个接口里直接写 API 请求。

文件：`backend/services/llm_service.py`

建议接口：

```python
class LLMService:
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        pass

    def generate_json(self, system_prompt: str, user_prompt: str, schema_name: str) -> dict:
        pass
```

要求：

- 从环境变量读取 API Key。
- 支持切换模型。
- 统一处理异常。
- 统一处理 JSON 提取与修复。
- 日志中不要打印完整 API Key。

环境变量示例：

```bash
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

或者：

```bash
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

---

## 8. Prompt 设计要求

### 8.1 通用要求

所有 prompt 必须强调：

```text
1. 必须输出合法 JSON。
2. 不要输出 Markdown。
3. 不要输出解释性文字。
4. 字段必须符合 Schema。
5. 如果信息不确定，可以填“未知”，不要编造过度细节。
```

---

### 8.2 character_extract.txt

```text
你是一个专业的小说改编分析助手。请根据用户提供的小说文本，提取主要人物信息。

要求：
1. 只输出合法 JSON，不要输出 Markdown，不要输出解释。
2. 必须符合以下结构：
{
  "characters": [
    {
      "name": "string",
      "role": "string",
      "personality": ["string"],
      "goal": "string",
      "first_appearance": "string",
      "relations": [
        {"target": "string", "relation": "string"}
      ],
      "evidence": "string"
    }
  ]
}
3. 只提取与剧情相关的重要人物。
4. evidence 必须来自原文或对原文的简短概括。
```

---

### 8.3 scene_plan.txt

```text
你是一个专业的影视编剧助手。请将小说内容改编为剧本分场大纲。

要求：
1. 只输出合法 JSON，不要输出 Markdown，不要输出解释。
2. 每一场必须有明确的时间、地点、出场人物、剧情目的和冲突点。
3. 不要直接生成完整剧本，只生成分场大纲。
4. 必须符合以下结构：
{
  "scenes": [
    {
      "scene_id": 1,
      "title": "string",
      "time": "string",
      "location": "string",
      "characters": ["string"],
      "plot_goal": "string",
      "conflict": "string",
      "source_paragraphs": [1]
    }
  ]
}
```

---

### 8.4 script_generate.txt

```text
你是一个专业的影视剧本创作助手。请根据场景大纲、人物档案和原文片段生成单场剧本。

要求：
1. 输出标准剧本格式。
2. 包含场景编号、时间、地点、人物、动作描写、对白。
3. 对白必须符合人物性格。
4. 不要改动核心剧情。
5. 可以适当补充镜头语言，但不要喧宾夺主。
6. 只生成当前这一场，不要生成其他场景。
```

---

### 8.5 consistency_check.txt

```text
你是一个专业的剧本审校助手。请检查生成剧本与人物档案、分场大纲之间是否存在一致性问题。

检查范围：
1. 人物名称是否前后不一致。
2. 人物是否出现在不合理的场景中。
3. 地点是否前后冲突。
4. 时间线是否冲突。
5. 角色性格是否突变。
6. 对白是否不符合人物设定。
7. 剧情是否缺少必要转场。

要求：
1. 只输出合法 JSON，不要输出 Markdown，不要输出解释。
2. 如果没有问题，返回 {"issues": []}。
3. 必须符合以下结构：
{
  "issues": [
    {
      "level": "high | medium | low",
      "type": "string",
      "scene_id": 1,
      "description": "string",
      "suggestion": "string"
    }
  ]
}
```

---

## 9. 前端页面设计

### 9.1 首页 / 导入页

页面目标：让评委一眼知道项目能做什么。

内容：

```text
标题：Novel2Script AI
副标题：结构化小说转剧本工作台
功能入口：上传小说 / 粘贴文本
示例按钮：加载示例小说
开始按钮：开始解析
```

---

### 9.2 工作台页面

建议采用左侧导航：

```text
1. 小说原文
2. 人物档案
3. 分场大纲
4. 剧本编辑
5. 一致性检查
6. 导出结果
```

---

### 9.3 人物卡片

每个角色展示为卡片：

```text
姓名：林川
身份：男主
性格：冷静、内敛、敏锐
目标：查清父亲失踪真相
关系：苏晚 / 合作伙伴
证据：……
```

---

### 9.4 场景卡片

每个场景展示为卡片：

```text
第 1 场：深夜来电
时间：夜晚
地点：林川的出租屋
人物：林川、苏晚
剧情目的：引出父亲失踪线索
冲突点：林川不愿相信苏晚
按钮：生成剧本
```

---

### 9.5 剧本编辑器

功能要求：

- 左侧显示场景列表。
- 右侧显示剧本内容。
- 支持编辑。
- 支持保存。
- 支持重新生成。

可以使用普通 textarea，不必集成复杂富文本编辑器。

---

### 9.6 检查报告页

使用不同颜色区分问题等级：

```text
high：严重问题
medium：中等问题
low：轻微问题
```

展示字段：

- 问题类型
- 所属场景
- 问题描述
- 修改建议

---

## 10. 72 小时开发计划

## Day 1：主流程跑通

目标：完成基础工程和前两个核心 AI 模块。

任务：

```text
1. 创建 GitHub/Gitee 仓库。
2. 初始化 backend 和 frontend 项目。
3. 实现 FastAPI 基础服务。
4. 实现 SQLite 数据库连接。
5. 实现小说导入接口。
6. 实现章节/段落解析。
7. 实现 LLMService。
8. 实现人物档案抽取。
9. 实现分场大纲生成。
10. 前端完成导入页、人物页、分场页。
```

Day 1 结束验收：

```text
输入小说文本后，可以看到人物卡片和分场大纲。
```

---

## Day 2：剧本生成与编辑

目标：完成剧本生成、编辑保存和基础导出。

任务：

```text
1. 实现单场剧本生成接口。
2. 实现剧本编辑保存接口。
3. 前端实现剧本编辑器。
4. 实现场景点击生成剧本。
5. 实现 Markdown 导出。
6. 增加示例小说。
7. 优化页面交互和加载状态。
```

Day 2 结束验收：

```text
可以从分场大纲生成单场剧本，修改后保存，并导出 Markdown。
```

---

## Day 3：创新点、文档与演示

目标：完成一致性检查、README、demo 视频和最终提交。

任务：

```text
1. 实现一致性检查接口。
2. 实现检查报告页面。
3. 完成 PDF 或 DOCX 导出，若时间不足只保留 Markdown。
4. 完成 README。
5. 完成 docs/architecture.md。
6. 补充接口文档 docs/api.md。
7. 录制 demo 视频。
8. 将 demo 视频链接写入 README。
9. 检查所有 PR 描述和 commit 记录。
10. 最终测试项目启动流程。
```

Day 3 结束验收：

```text
完整 demo 流程可运行：导入小说 → 人物抽取 → 分场大纲 → 剧本生成 → 编辑保存 → 一致性检查 → 导出。
```

---

## 11. PR 拆分要求

评审明确要求看 PR 数量和质量，因此必须持续提交，不能最后一次性提交。

建议拆成以下 PR：

```text
PR 1：初始化项目结构与前后端基础环境
PR 2：实现小说文本导入与章节段落解析
PR 3：实现 LLMService 与 Prompt 管理
PR 4：实现人物档案抽取与角色卡展示
PR 5：实现分场大纲生成与场景列表展示
PR 6：实现单场剧本生成与编辑保存
PR 7：实现一致性检查与问题报告
PR 8：实现 Markdown 导出与示例数据
PR 9：优化 UI、完善 README 与 demo 文档
```

### PR 描述模板

每个 PR 使用以下模板：

```markdown
## 功能描述

本 PR 实现……

## 实现思路

- ……
- ……

## 测试方式

1. 启动后端：`uvicorn main:app --reload --port 8000`
2. 启动前端：`npm run dev`
3. 打开页面并执行……

## 影响范围

- backend/...
- frontend/...
```

---

## 12. README 必须包含的内容

README 至少包含以下部分：

```markdown
# Novel2Script AI

## 项目简介

## 项目亮点

## 功能演示

## 技术架构

## 快速启动

## 环境变量配置

## 项目结构

## 核心功能

## API 接口

## 示例数据

## Demo 视频

## 开发过程与 PR 记录

## 未来规划
```

### 项目亮点建议写法

```markdown
## 项目亮点

1. 多阶段小说改编流程  
   本项目不是直接将小说交给大模型生成剧本，而是将改编过程拆解为人物抽取、剧情分场、剧本生成和一致性检查等多个阶段。

2. 结构化 Schema 约束  
   系统要求大模型按照固定 JSON Schema 输出人物、场景和检查报告，提升结果稳定性和可编辑性。

3. 人物一致性维护  
   系统自动维护人物档案，并在生成剧本后检查人物名称、性格、关系和对白风格是否一致。

4. 分场式剧本生成  
   支持按场景逐步生成剧本，用户可以对单个场景进行编辑、保存和导出。

5. 可解释的检查报告  
   系统会指出潜在剧情冲突、时间线问题和人物设定不一致问题，辅助创作者二次修改。
```

---

## 13. Demo 视频脚本

视频建议 3 到 5 分钟。

录制流程：

```text
1. 打开项目首页，介绍项目：Novel2Script AI，结构化小说转剧本工作台。
2. 粘贴或加载示例小说文本。
3. 点击“开始解析”。
4. 展示章节和段落解析结果。
5. 展示人物档案卡片。
6. 展示分场大纲，每一场包含时间、地点、人物、剧情目的和冲突点。
7. 点击第 1 场“生成剧本”。
8. 展示生成的剧本内容。
9. 手动修改一句对白并保存。
10. 点击“一致性检查”。
11. 展示问题报告。
12. 点击导出 Markdown。
13. 打开导出的 Markdown 文件。
14. 最后展示 GitHub/Gitee 仓库、README、PR 记录。
```

讲解重点：

```text
这个项目不是简单调用 AI 生成文本，而是把小说改编拆成结构化工作流：人物建模、剧情分场、单场剧本生成、一致性检查和导出。系统通过 JSON Schema 约束 AI 输出，使结果更加稳定、可编辑、可检查。
```

---

## 14. 最小可行版本要求

如果时间不足，必须优先完成以下功能：

```text
1. 小说文本输入
2. 人物档案抽取
3. 分场大纲生成
4. 单场剧本生成
5. 剧本编辑保存
6. 一致性检查
7. Markdown 导出
8. README
9. Demo 视频
```

可以暂时放弃：

```text
1. 登录注册
2. 多用户系统
3. 复杂权限控制
4. 支付功能
5. 高级富文本编辑器
6. 复杂协同编辑
```

---

## 15. 质量要求

### 15.1 代码质量

- 每个模块职责清晰。
- AI 调用统一封装。
- Prompt 独立管理。
- 后端接口命名规范。
- 前端组件拆分清晰。
- 必须有基础异常处理。
- README 必须能指导评委成功运行项目。

### 15.2 可演示性

必须保证：

- 没有 API Key 时，项目可以使用 mock 数据演示。
- 有 API Key 时，项目可以真实调用模型。
- 示例小说不能太长，建议 800 到 1500 字，方便快速生成。
- 每个按钮点击后要有 loading 状态。
- 出错时要有清晰提示。

### 15.3 Mock 模式

为了避免演示时 API 不稳定，必须实现 mock 模式。

环境变量：

```bash
USE_MOCK_LLM=true
```

当 `USE_MOCK_LLM=true` 时：

- 人物抽取返回固定示例人物。
- 分场大纲返回固定示例场景。
- 剧本生成返回固定示例剧本。
- 一致性检查返回固定示例报告。

这样 demo 视频和评委运行都更稳定。

---

## 16. 验收标准

最终项目必须满足：

```text
1. 前后端可以正常启动。
2. 可以导入小说文本。
3. 可以生成并展示人物档案。
4. 可以生成并展示分场大纲。
5. 可以针对单个场景生成剧本。
6. 可以编辑并保存剧本。
7. 可以生成一致性检查报告。
8. 可以导出 Markdown 文件。
9. README 完整。
10. demo 视频可播放。
11. PR 和 commit 记录连续、清晰。
```

---

## 17. 开发优先级

按照以下顺序开发：

```text
P0：项目初始化、小说导入、LLMService、人物抽取、分场大纲
P1：剧本生成、剧本编辑保存、Markdown 导出
P2：一致性检查、Mock 模式、UI 优化
P3：PDF/DOCX 导出、版本对比、人物关系图
```

不要先做 P3。

---

## 18. 可选加分功能

如果核心功能完成后还有时间，可以做：

```text
1. 人物关系图
2. 剧情时间线
3. 多风格剧本生成：短剧 / 电影 / 舞台剧
4. 剧本版本对比
5. 人物对白风格重写
6. 场景拖拽排序
7. 一键生成 README 中的示例输出
```

优先推荐：

```text
1. 人物关系图
2. 多风格剧本生成
3. 剧本版本对比
```

---

## 19. 给 Codex 的执行要求

请按照以下原则协助开发：

```text
1. 优先保证项目可以运行，不要过度设计。
2. 每次只实现一个明确功能，方便拆 PR。
3. 后端先完成 API，再做前端调用。
4. 所有 LLM 输出必须尽量结构化。
5. 所有接口必须有基础错误处理。
6. 如果真实 LLM API 不可用，必须支持 mock 模式。
7. 不要加入登录注册等非核心功能。
8. 不要把所有逻辑写在 main.py 中，要按 routers/services/models 拆分。
9. README 和示例数据必须同步维护。
10. 每完成一个功能，写清楚如何测试。
```

---

## 20. 第一阶段立即执行任务

请 Codex 从以下任务开始：

```text
1. 创建项目目录结构。
2. 初始化 backend FastAPI 项目。
3. 初始化 frontend Vue3 + Vite 项目。
4. 后端实现 /api/health 健康检查接口。
5. 后端实现 SQLite 数据库连接。
6. 后端实现 novels 表和小说导入接口。
7. 前端实现首页和小说输入表单。
8. 前后端联调小说导入接口。
9. 添加 examples/demo_novel.txt。
10. 更新 README 的启动说明。
```

完成后继续第二阶段：人物抽取与分场大纲生成。

---

## 21. 备注

本项目的核心竞争力不是“AI 能写剧本”，而是：

```text
结构化改编流程
可编辑分场工作台
人物一致性维护
剧情逻辑检查
可导出的完整剧本结果
```

开发过程中，始终围绕这几个关键词设计功能和 demo。
