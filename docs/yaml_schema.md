# 剧本 YAML Schema

本项目的核心交付物是可编辑的结构化剧本 YAML。YAML 比纯文本更适合小说改编工作流，因为它既能被作者直接阅读和修改，也能被程序继续解析、二次编辑和导出。

## Schema 示例

```yaml
schema_version: "1.0"
project:
  id: 18
  title: "倾覆之塔"
  type: "novel_to_script"
  language: "zh-CN"
source:
  kind: "novel"
  minimum_chapters_required: 3
adaptation_strategy:
  content: |-
    核心改编原则
    围绕主角目标和高情绪冲突组织分场。
characters:
  -
    id: 1
    name: "罗素"
    role: "主角"
    personality:
      - "谨慎"
    goal: "抵达幸福岛并理解自己的处境"
    first_appearance: "第一章 灰穹"
    relations: []
    evidence: "原文证据或摘要"
scenes:
  -
    scene_id: 1
    title: "头等舱初遇"
    time: "白天"
    location: "空艇头等舱"
    characters:
      - "罗素"
      - "白毛青年"
    beat:
      plot_goal: "建立罗素与白毛青年的首次互动"
      conflict: "罗素保持警惕，白毛青年主动试探"
    source_paragraphs:
      - 106429
      - 106430
    script:
      version: 1
      format: "plain_text"
      content: |-
        第 1 场 头等舱初遇

        时间：白天
        地点：空艇头等舱
        人物：罗素、白毛青年

        【内景，空艇头等舱，白天】
        ...
```

## 字段定义

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `schema_version` | string | 是 | Schema 版本，便于后续兼容升级。 |
| `project` | object | 是 | 剧本项目元信息。 |
| `project.id` | number | 是 | 系统内小说项目 ID。 |
| `project.title` | string | 是 | 小说或改编项目标题。 |
| `project.type` | string | 是 | 固定为 `novel_to_script`。 |
| `project.language` | string | 是 | 内容语言，默认 `zh-CN`。 |
| `source` | object | 是 | 原始输入约束。 |
| `source.kind` | string | 是 | 固定为 `novel`。 |
| `source.minimum_chapters_required` | number | 是 | 题目要求至少 3 个章节。 |
| `adaptation_strategy` | object | 是 | 改编策略层，用于约束后续分场和剧本生成。 |
| `adaptation_strategy.content` | string | 是 | 主线保留、删减原则、世界观呈现和情绪节奏策略。 |
| `characters` | array | 是 | 人物档案列表。 |
| `characters[].name` | string | 是 | 人物姓名。 |
| `characters[].role` | string | 是 | 角色定位。 |
| `characters[].personality` | array | 是 | 性格标签。 |
| `characters[].goal` | string | 是 | 人物目标。 |
| `characters[].relations` | array | 是 | 与其他人物的关系。 |
| `characters[].evidence` | string | 是 | 原文证据或摘要，避免人物设定失真。 |
| `scenes` | array | 是 | 分场剧本列表。 |
| `scenes[].scene_id` | number | 是 | 剧本内场次编号。 |
| `scenes[].title` | string | 是 | 场景标题。 |
| `scenes[].time` | string | 是 | 场景时间。 |
| `scenes[].location` | string | 是 | 场景地点。 |
| `scenes[].characters` | array | 是 | 本场出场人物。 |
| `scenes[].beat` | object | 是 | 场景节拍，参考 Dramatron 的 `plot_element / beat` 思路。 |
| `scenes[].beat.plot_goal` | string | 是 | 本场剧情目的。 |
| `scenes[].beat.conflict` | string | 是 | 本场冲突。 |
| `scenes[].source_paragraphs` | array | 是 | 对应原文段落 ID，用于追溯每场改编来源。 |
| `scenes[].script` | object | 是 | 当前场景剧本文本。 |
| `scenes[].script.version` | number/null | 是 | 剧本版本号，未生成时为 `null`。 |
| `scenes[].script.format` | string | 是 | 当前为 `plain_text`。 |
| `scenes[].script.content` | string | 是 | 可编辑剧本正文。 |

## 设计原因

1. 分层表达小说改编过程  
   小说不能直接变成一整段剧本。Schema 将改编拆成 `adaptation_strategy`、`characters`、`scenes`、`beat` 和 `script`，对应改编决策、人物建模、分场大纲和单场剧本生成。

2. 保留可追溯证据  
   `source_paragraphs` 和人物 `evidence` 让作者知道每个场景和人物设定来自哪里，便于回到原文校对。

3. 支持作者编辑  
   `script.content` 使用纯文本块，作者可以直接修改；`version` 用于后续版本管理。

4. 支持后续自动化处理  
   `characters`、`location`、`time`、`beat` 和 `script` 都是结构化字段，后续可以继续用于版本管理、格式转换或人工精修，而不是只保留一段不可解析的文本。

5. 贴合 Dramatron 的层级思想  
   Dramatron 使用 `Scene(place, plot_element, beat)` 作为生成对白前的中间结构。本 Schema 将 `location`、`beat.plot_goal` 和 `beat.conflict` 固化下来，让小说改编结果既可读，也能继续驱动单场剧本生成。

6. 保留改编策略层  
   小说改编需要先明确故事核心、主线保留、删减原则和情绪节奏，再进入剧本生成。本 Schema 保留 `adaptation_strategy.content`，让后续分场和单场剧本生成有明确依据。
