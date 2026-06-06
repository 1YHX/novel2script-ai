<template>
  <section class="board-page">
    <header class="board-toolbar">
      <div>
        <h2>导出结果</h2>
        <p v-if="currentNovel">当前项目：{{ currentNovel.title }}（ID: {{ currentNovel.novel_id }}）</p>
        <p v-else>请先完成小说导入</p>
      </div>
      <div class="toolbar-actions">
        <el-button type="primary" :disabled="!currentNovel" :loading="loadingFormat === 'yaml'" @click="downloadYaml">
          导出 YAML
        </el-button>
        <el-button type="primary" :disabled="!currentNovel" :loading="loading" @click="downloadMarkdown">
          导出 Markdown
        </el-button>
      </div>
    </header>

    <div class="export-layout">
      <div class="export-format">
        <h3>YAML</h3>
        <p>题目要求的结构化剧本格式，包含人物档案、分场节拍、剧本文本和原文段落追溯。</p>
      </div>
      <div class="export-format">
        <h3>Markdown</h3>
        <p>包含人物档案、分场大纲和完整剧本，适合演示和提交。</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

import { exportMarkdown, exportYaml } from '../api'
import { currentNovel } from '../store/workspace'

const loading = ref(false)
const loadingFormat = ref('')

async function downloadYaml() {
  if (!currentNovel.value) return

  loadingFormat.value = 'yaml'
  try {
    const response = await exportYaml(currentNovel.value.novel_id)
    downloadBlob(response.data, `${currentNovel.value.title || 'novel2script'}.yaml`, 'application/yaml;charset=utf-8')
    ElMessage.success('YAML 已导出')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '导出失败')
  } finally {
    loadingFormat.value = ''
  }
}

async function downloadMarkdown() {
  if (!currentNovel.value) return

  loading.value = true
  try {
    const response = await exportMarkdown(currentNovel.value.novel_id)
    downloadBlob(response.data, `${currentNovel.value.title || 'novel2script'}.md`, 'text/markdown;charset=utf-8')
    ElMessage.success('Markdown 已导出')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '导出失败')
  } finally {
    loading.value = false
  }
}

function downloadBlob(data, filename, type) {
  const blob = new Blob([data], { type })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
</script>
