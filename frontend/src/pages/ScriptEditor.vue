<template>
  <section class="script-editor-page">
    <header class="board-toolbar">
      <div>
        <h2>剧本编辑</h2>
        <p v-if="currentNovel">当前项目：{{ currentNovel.title }}（ID: {{ currentNovel.novel_id }}）</p>
        <p v-else>请先完成小说导入和分场大纲</p>
      </div>
      <div class="toolbar-actions">
        <el-button :disabled="!currentNovel || batchGenerating" @click="loadScenes">刷新场景</el-button>
        <el-button
          type="primary"
          :disabled="!currentNovel || scenes.length === 0 || ungeneratedScenes.length === 0"
          :loading="batchGenerating"
          @click="handleBatchGenerate"
        >
          {{ batchGenerating ? '批量生成中' : '批量生成未生成' }}
        </el-button>
      </div>
    </header>

    <div v-if="currentNovel && scenes.length > 0" class="script-batch-status">
      <span>已生成 {{ generatedCount }} / {{ scenes.length }} 场</span>
      <el-progress :percentage="batchProgress" :show-text="false" />
    </div>

    <div v-if="!currentNovel" class="panel-placeholder">
      导入小说并生成分场后即可编辑单场剧本
    </div>
    <div v-else class="script-editor-layout">
      <aside class="scene-list">
        <button
          v-for="(scene, index) in scenes"
          :key="scene.scene_id"
          class="scene-list-item"
          :class="{ active: selectedScene?.scene_id === scene.scene_id }"
          @click="selectScene(scene)"
        >
          <span class="scene-list-row">
            <span>第 {{ index + 1 }} 场</span>
            <em :class="{ ready: scriptStatus[scene.scene_id] }">
              {{ scriptStatus[scene.scene_id] ? `v${scriptStatus[scene.scene_id].version}` : '未生成' }}
            </em>
          </span>
          <strong>{{ scene.title }}</strong>
          <small>{{ scene.time }} / {{ scene.location }}</small>
        </button>
        <div v-if="scenes.length === 0" class="empty-list">请先生成分场大纲</div>
      </aside>

      <section class="script-panel">
        <div v-if="!selectedScene" class="panel-placeholder">
          从左侧选择一个场景
        </div>
        <template v-else>
          <div class="script-controls">
            <div>
              <h3>{{ selectedScene.title }}</h3>
              <p>{{ selectedScene.time }} / {{ selectedScene.location }}</p>
            </div>
            <div class="toolbar-actions">
              <el-select v-model="style" class="style-select" placeholder="剧本风格">
                <el-option label="短剧风格" value="短剧风格" />
                <el-option label="悬疑紧凑" value="悬疑紧凑" />
                <el-option label="情感细腻" value="情感细腻" />
                <el-option label="高燃爽剧" value="高燃爽剧" />
                <el-option label="轻喜剧" value="轻喜剧" />
                <el-option label="影视剧风格" value="影视剧风格" />
                <el-option label="古装对白" value="古装对白" />
              </el-select>
              <el-select v-model="dialogueDensity" class="density-select" placeholder="对白密度">
                <el-option label="对白精简" value="low" />
                <el-option label="对白适中" value="medium" />
                <el-option label="对白密集" value="high" />
              </el-select>
              <el-switch
                v-model="includeCameraLanguage"
                inline-prompt
                active-text="镜头"
                inactive-text="无镜头"
              />
              <el-button
                :type="script ? 'default' : 'primary'"
                :loading="generating"
                :disabled="batchGenerating"
                @click="handleGenerate"
              >
                {{ script ? '重新生成' : '生成剧本' }}
              </el-button>
              <el-button type="primary" :disabled="!script" :loading="saving" @click="handleSave">保存修改</el-button>
            </div>
          </div>

          <div v-if="!script" class="script-empty-state">
            当前场景还没有剧本，可直接在本页生成，不需要回到分场大纲。
          </div>

          <el-input
            v-model="content"
            type="textarea"
            :rows="22"
            placeholder="点击“生成剧本”后在这里编辑内容"
          />
          <p v-if="script" class="script-meta">当前版本：v{{ script.version }}</p>
        </template>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import { generateScript, getScenes, getScript, updateScript } from '../api'
import { activeTab, currentNovel, selectedSceneId } from '../store/workspace'

const scenes = ref([])
const selectedScene = ref(null)
const script = ref(null)
const scriptStatus = ref({})
const content = ref('')
const style = ref('短剧风格')
const dialogueDensity = ref('medium')
const includeCameraLanguage = ref(true)
const generating = ref(false)
const batchGenerating = ref(false)
const saving = ref(false)

const generatedCount = computed(() => Object.keys(scriptStatus.value).length)
const ungeneratedScenes = computed(() => scenes.value.filter((scene) => !scriptStatus.value[scene.scene_id]))
const batchProgress = computed(() => {
  if (scenes.value.length === 0) return 0
  return Math.round((generatedCount.value / scenes.value.length) * 100)
})

watch(
  currentNovel,
  () => {
    scenes.value = []
    selectedScene.value = null
    script.value = null
    scriptStatus.value = {}
    content.value = ''
    if (currentNovel.value) {
      loadScenes()
    }
  },
  { immediate: true }
)

watch(
  selectedSceneId,
  async (sceneId) => {
    if (!sceneId) return
    if (scenes.value.length === 0) {
      await loadScenes()
    }
    await nextTick()
    const scene = scenes.value.find((item) => item.scene_id === sceneId)
    if (scene) {
      await selectScene(scene)
    }
  },
  { immediate: true }
)

watch(
  activeTab,
  (tabName) => {
    if (tabName === 'scripts' && currentNovel.value) {
      loadScenes({ forceSelectFirst: scenes.value.length === 0 })
    }
  },
  { immediate: true }
)

async function loadScenes(options = {}) {
  if (!currentNovel.value) return

  try {
    const response = await getScenes(currentNovel.value.novel_id)
    scenes.value = response.data.scenes
    await loadScriptStatus()
    const shouldSelectFirst = options.forceSelectFirst || !selectedScene.value
    if (selectedSceneId.value && shouldSelectFirst) {
      const scene = scenes.value.find((item) => item.scene_id === selectedSceneId.value)
      if (scene) {
        await selectScene(scene)
      }
    } else if (shouldSelectFirst && scenes.value.length > 0) {
      await selectScene(scenes.value[0])
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '读取场景失败')
  }
}

async function loadScriptStatus() {
  const entries = await Promise.allSettled(
    scenes.value.map(async (scene) => {
      const response = await getScript(scene.scene_id)
      return [scene.scene_id, response.data]
    })
  )

  const nextStatus = {}
  for (const entry of entries) {
    if (entry.status === 'fulfilled') {
      const [sceneId, latestScript] = entry.value
      nextStatus[sceneId] = latestScript
    }
  }
  scriptStatus.value = nextStatus
}

async function selectScene(scene) {
  selectedScene.value = scene
  script.value = null
  content.value = ''

  try {
    const response = await getScript(scene.scene_id)
    script.value = response.data
    content.value = response.data.content
  } catch (error) {
    if (error.response?.status !== 404) {
      ElMessage.error(error.response?.data?.detail || '读取剧本失败')
    }
  }
}

async function handleGenerate() {
  if (!selectedScene.value) return

  generating.value = true
  try {
    const generatedScript = await generateSceneScript(selectedScene.value)
    script.value = generatedScript
    content.value = generatedScript.content
    ElMessage.success('剧本已生成')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成剧本失败')
  } finally {
    generating.value = false
  }
}

async function handleBatchGenerate() {
  if (ungeneratedScenes.value.length === 0) return

  batchGenerating.value = true
  let successCount = 0
  try {
    for (const scene of ungeneratedScenes.value) {
      const generatedScript = await generateSceneScript(scene)
      successCount += 1
      if (!selectedScene.value || selectedScene.value.scene_id === scene.scene_id) {
        selectedScene.value = scene
        script.value = generatedScript
        content.value = generatedScript.content
      }
    }
    ElMessage.success(`批量生成完成，共生成 ${successCount} 场`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || `批量生成中断，已完成 ${successCount} 场`)
  } finally {
    batchGenerating.value = false
  }
}

async function generateSceneScript(scene) {
  const response = await generateScript(scene.scene_id, {
    style: style.value,
    dialogue_density: dialogueDensity.value,
    include_camera_language: includeCameraLanguage.value
  })
  scriptStatus.value = {
    ...scriptStatus.value,
    [scene.scene_id]: response.data
  }
  return response.data
}

async function handleSave() {
  if (!script.value) return
  if (!content.value.trim()) {
    ElMessage.error('剧本内容不能为空')
    return
  }

  saving.value = true
  try {
    const response = await updateScript(script.value.script_id, { content: content.value })
    script.value = response.data
    scriptStatus.value = {
      ...scriptStatus.value,
      [selectedScene.value.scene_id]: response.data
    }
    content.value = response.data.content
    ElMessage.success('修改已保存')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存剧本失败')
  } finally {
    saving.value = false
  }
}
</script>
