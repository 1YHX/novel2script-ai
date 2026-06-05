<template>
  <section class="board-page">
    <header class="board-toolbar">
      <div>
        <h2>一致性检查</h2>
        <p v-if="currentNovel">当前项目：{{ currentNovel.title }}（ID: {{ currentNovel.novel_id }}）</p>
        <p v-else>请先完成小说导入</p>
      </div>
      <div class="toolbar-actions">
        <el-button :disabled="!currentNovel" @click="loadReport">刷新报告</el-button>
        <el-button type="primary" :disabled="!currentNovel" :loading="loading" @click="handleCheck">
          开始检查
        </el-button>
      </div>
    </header>

    <div v-if="!currentNovel" class="panel-placeholder">
      生成剧本后即可运行一致性检查
    </div>
    <div v-else-if="issues.length === 0" class="panel-placeholder">
      暂无问题报告，点击“开始检查”生成
    </div>
    <div v-else class="issue-list">
      <IssueCard v-for="(issue, index) in issues" :key="index" :issue="issue" />
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import { getCheckReport, runConsistencyCheck } from '../api'
import IssueCard from '../components/IssueCard.vue'
import { currentNovel } from '../store/workspace'

const loading = ref(false)
const issues = ref([])

watch(
  currentNovel,
  () => {
    issues.value = []
    if (currentNovel.value) {
      loadReport()
    }
  },
  { immediate: true }
)

async function loadReport() {
  if (!currentNovel.value) return

  try {
    const response = await getCheckReport(currentNovel.value.novel_id)
    issues.value = response.data.issues
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '读取检查报告失败')
  }
}

async function handleCheck() {
  if (!currentNovel.value) return

  loading.value = true
  try {
    const response = await runConsistencyCheck(currentNovel.value.novel_id)
    issues.value = response.data.issues
    ElMessage.success(issues.value.length ? '检查完成，发现潜在问题' : '检查完成，未发现问题')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '一致性检查失败')
  } finally {
    loading.value = false
  }
}
</script>
