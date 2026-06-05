<template>
  <section class="board-page">
    <header class="board-toolbar">
      <div>
        <h2>人物档案</h2>
        <p v-if="currentNovel">当前项目：{{ currentNovel.title }}</p>
        <p v-else>请先在小说导入页完成解析</p>
      </div>
      <div class="toolbar-actions">
        <el-button :disabled="!currentNovel" @click="loadCharacters">刷新</el-button>
        <el-button type="primary" :disabled="!currentNovel" :loading="loading" @click="handleExtract">
          抽取人物
        </el-button>
      </div>
    </header>

    <div v-if="!currentNovel" class="panel-placeholder">
      导入小说后即可抽取人物档案
    </div>
    <div v-else-if="characters.length === 0" class="panel-placeholder">
      暂无人物档案，点击“抽取人物”生成
    </div>
    <div v-else class="character-grid">
      <CharacterCard v-for="character in characters" :key="character.id" :character="character" />
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import { extractCharacters, getCharacters } from '../api'
import CharacterCard from '../components/CharacterCard.vue'
import { currentNovel } from '../store/workspace'

const loading = ref(false)
const characters = ref([])

watch(
  currentNovel,
  () => {
    characters.value = []
    if (currentNovel.value) {
      loadCharacters()
    }
  },
  { immediate: true }
)

async function loadCharacters() {
  if (!currentNovel.value) return

  try {
    const response = await getCharacters(currentNovel.value.novel_id)
    characters.value = response.data.characters
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '读取人物档案失败')
  }
}

async function handleExtract() {
  if (!currentNovel.value) return

  loading.value = true
  try {
    const response = await extractCharacters(currentNovel.value.novel_id)
    characters.value = response.data.characters
    ElMessage.success('人物档案已生成')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '人物抽取失败')
  } finally {
    loading.value = false
  }
}
</script>
