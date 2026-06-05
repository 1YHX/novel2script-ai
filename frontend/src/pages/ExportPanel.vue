<template>
  <section class="board-page">
    <header class="board-toolbar">
      <div>
        <h2>导出结果</h2>
        <p v-if="currentNovel">当前项目：{{ currentNovel.title }}（ID: {{ currentNovel.novel_id }}）</p>
        <p v-else>请先完成小说导入</p>
      </div>
      <div class="toolbar-actions">
        <el-button type="primary" :disabled="!currentNovel" :loading="loading" @click="downloadMarkdown">
          导出 Markdown
        </el-button>
      </div>
    </header>

    <div class="export-layout">
      <div class="export-format">
        <h3>Markdown</h3>
        <p>包含人物档案、分场大纲、完整剧本和一致性检查报告，适合演示和提交。</p>
      </div>
      <div class="export-format muted">
        <h3>PDF / DOCX</h3>
        <p>后续可扩展；当前优先保证核心闭环稳定运行。</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

import { exportMarkdown } from '../api'
import { currentNovel } from '../store/workspace'

const loading = ref(false)

async function downloadMarkdown() {
  if (!currentNovel.value) return

  loading.value = true
  try {
    const response = await exportMarkdown(currentNovel.value.novel_id)
    const blob = new Blob([response.data], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${currentNovel.value.title || 'novel2script'}.md`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('Markdown 已导出')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '导出失败')
  } finally {
    loading.value = false
  }
}
</script>
