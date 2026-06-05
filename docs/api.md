# API 文档

## GET /api/health

健康检查接口。

响应：

```json
{
  "status": "ok",
  "service": "novel2script-ai"
}
```

## POST /api/novels/import

导入小说并解析章节、段落。

请求：

```json
{
  "title": "示例小说",
  "content": "第一章 雨夜\n林川接到了一个陌生电话……"
}
```

## POST /api/characters/extract/{novel_id}

抽取人物档案并保存。

## GET /api/characters/{novel_id}

读取小说的人物档案。

## POST /api/scenes/plan/{novel_id}

生成分场大纲，支持查询参数 `scene_count`，默认 5。

## GET /api/scenes/{novel_id}

读取小说的分场大纲。

## POST /api/scripts/generate/{scene_id}

生成单场剧本。

请求：

```json
{
  "style": "短剧风格",
  "dialogue_density": "medium",
  "include_camera_language": true
}
```

## GET /api/scripts/{scene_id}

读取某个场景最新版本剧本。

## PUT /api/scripts/{script_id}

保存编辑后的剧本内容，并生成新版本。

## POST /api/check/consistency/{novel_id}

检查人物档案、分场大纲和已生成剧本的一致性。

## GET /api/check/reports/{novel_id}

读取最新一致性检查报告。

## GET /api/export/markdown/{novel_id}

导出 Markdown 文件，包含人物档案、分场大纲、完整剧本和一致性检查报告。
