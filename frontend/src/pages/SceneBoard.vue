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
        <el-button :disabled="!currentNovel" :loading="strategyLoading" @click="handleGenerateStrategy">
          生成改编策略
        </el-button>
        <el-button type="primary" :disabled="!currentNovel" :loading="loading" @click="handlePlan">
          生成分场
        </el-button>
      </div>
    </header>

    <div v-if="!currentNovel" class="panel-placeholder">
      导入小说后即可生成分场大纲
    </div>
    <div v-else>
      <section class="strategy-panel">
        <div class="strategy-panel-header">
          <div>
            <h3>改编策略</h3>
            <p>参考 Toonflow 的策略层，为分场和剧本生成提供主线、删减和节奏约束。</p>
          </div>
        </div>
        <pre v-if="strategy">{{ strategy.content }}</pre>
        <div v-else class="strategy-empty">暂无改编策略，可先生成策略，再生成分场。</div>
      </section>

      <div v-if="scenes.length === 0" class="panel-placeholder">
        暂无分场大纲，点击“生成分场”开始规划
      </div>
      <div v-else class="scene-grid">
        <SceneCard
          v-for="(scene, index) in scenes"
          :key="scene.scene_id"
          :scene="scene"
          :index="index"
          :generating="generatingSceneId === scene.scene_id"
          :script="generatedScripts[scene.scene_id]"
          @generate="handleGenerateScript"
          @open-script="handleOpenScript"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import { generateScript, generateStrategy, getScenes, getStrategy, planScenes } from '../api'
import SceneCard from '../components/SceneCard.vue'
import { currentNovel, openScriptEditor } from '../store/workspace'

const loading = ref(false)
const sceneCount = ref(5)
const scenes = ref([])
const generatingSceneId = ref(null)
const generatedScripts = ref({})
const strategy = ref(null)
const strategyLoading = ref(false)

watch(
  currentNovel,
  () => {
    scenes.value = []
    generatedScripts.value = {}
    strategy.value = null
    if (currentNovel.value) {
      loadScenes()
      loadStrategy()
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

async function loadStrategy() {
  if (!currentNovel.value) return

  try {
    const response = await getStrategy(currentNovel.value.novel_id)
    strategy.value = response.data
  } catch (error) {
    if (error.response?.status !== 404) {
      ElMessage.error(error.response?.data?.detail || '读取改编策略失败')
    }
  }
}

async function handleGenerateStrategy() {
  if (!currentNovel.value) return

  strategyLoading.value = true
  try {
    const response = await generateStrategy(currentNovel.value.novel_id)
    strategy.value = response.data
    ElMessage.success('改编策略已生成')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成改编策略失败')
  } finally {
    strategyLoading.value = false
  }
}

async function handlePlan() {
  if (!currentNovel.value) return

  loading.value = true
  try {
    const response = await planScenes(currentNovel.value.novel_id, sceneCount.value)
    scenes.value = response.data.scenes
    generatedScripts.value = {}
    ElMessage.success('分场大纲已生成')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成分场失败')
  } finally {
    loading.value = false
  }
}

async function handleGenerateScript(scene) {
  generatingSceneId.value = scene.scene_id
  try {
    const response = await generateScript(scene.scene_id, {
      style: '短剧风格',
      dialogue_density: 'medium',
      include_camera_language: true
    })
    generatedScripts.value = {
      ...generatedScripts.value,
      [scene.scene_id]: response.data
    }
    ElMessage.success(`《${scene.title}》剧本已生成，已在当前卡片下方显示`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成剧本失败')
  } finally {
    generatingSceneId.value = null
  }
}

function handleOpenScript(scene) {
  openScriptEditor(scene.scene_id)
}
</script>
