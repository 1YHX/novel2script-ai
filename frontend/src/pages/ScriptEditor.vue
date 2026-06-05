<template>
  <section class="script-editor-page">
    <header class="board-toolbar">
      <div>
        <h2>剧本编辑</h2>
        <p v-if="currentNovel">当前项目：{{ currentNovel.title }}</p>
        <p v-else>请先完成小说导入和分场大纲</p>
      </div>
      <div class="toolbar-actions">
        <el-button :disabled="!currentNovel" @click="loadScenes">刷新场景</el-button>
      </div>
    </header>

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
          <span>第 {{ index + 1 }} 场</span>
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
              <el-select v-model="style" class="style-select">
                <el-option label="短剧风格" value="短剧风格" />
                <el-option label="电影风格" value="电影风格" />
                <el-option label="舞台剧风格" value="舞台剧风格" />
              </el-select>
              <el-button :loading="generating" @click="handleGenerate">生成剧本</el-button>
              <el-button type="primary" :disabled="!script" :loading="saving" @click="handleSave">保存修改</el-button>
            </div>
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
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import { generateScript, getScenes, getScript, updateScript } from '../api'
import { currentNovel } from '../store/workspace'

const scenes = ref([])
const selectedScene = ref(null)
const script = ref(null)
const content = ref('')
const style = ref('短剧风格')
const generating = ref(false)
const saving = ref(false)

watch(
  currentNovel,
  () => {
    scenes.value = []
    selectedScene.value = null
    script.value = null
    content.value = ''
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
    ElMessage.error(error.response?.data?.detail || '读取场景失败')
  }
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
    const response = await generateScript(selectedScene.value.scene_id, {
      style: style.value,
      dialogue_density: 'medium',
      include_camera_language: true
    })
    script.value = response.data
    content.value = response.data.content
    ElMessage.success('剧本已生成')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成剧本失败')
  } finally {
    generating.value = false
  }
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
    content.value = response.data.content
    ElMessage.success('修改已保存')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存剧本失败')
  } finally {
    saving.value = false
  }
}
</script>
