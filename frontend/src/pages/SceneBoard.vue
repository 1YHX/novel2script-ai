<template>
  <section class="board-page">
    <header class="board-toolbar">
      <div>
        <h2>分场大纲</h2>
        <p v-if="currentNovel">当前项目：{{ currentNovel.title }}（ID: {{ currentNovel.novel_id }}）</p>
        <p v-else>请先在小说导入页完成解析</p>
      </div>
      <div class="toolbar-actions scene-actions">
        <el-input-number v-model="sceneCount" :min="1" :max="20" :disabled="!currentNovel || loading" />
        <el-button :disabled="!currentNovel" @click="loadScenes">刷新</el-button>
        <el-button type="primary" :disabled="!currentNovel" :loading="loading" @click="handlePlan">
          生成分场
        </el-button>
      </div>
    </header>

    <div v-if="!currentNovel" class="panel-placeholder">
      导入小说后即可生成分场大纲
    </div>
    <div v-else-if="scenes.length === 0" class="panel-placeholder">
      暂无分场大纲，点击“生成分场”开始规划
    </div>
    <div v-else class="scene-grid">
      <SceneCard v-for="(scene, index) in scenes" :key="scene.scene_id" :scene="scene" :index="index" />
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import { getScenes, planScenes } from '../api'
import SceneCard from '../components/SceneCard.vue'
import { currentNovel } from '../store/workspace'

const loading = ref(false)
const sceneCount = ref(5)
const scenes = ref([])

watch(
  currentNovel,
  () => {
    scenes.value = []
    if (currentNovel.value) {
      loadScenes()
    }
  },
  { immediate: true }
)

async function loadScenes() {
  if (!currentNovel.value) return

  try {
    const response = await getScenes(currentNovel.value.novel_id)
    scenes.value = response.data.scenes
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '读取分场大纲失败')
  }
}

async function handlePlan() {
  if (!currentNovel.value) return

  loading.value = true
  try {
    const response = await planScenes(currentNovel.value.novel_id, sceneCount.value)
    scenes.value = response.data.scenes
    ElMessage.success('分场大纲已生成')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成分场失败')
  } finally {
    loading.value = false
  }
}
</script>
