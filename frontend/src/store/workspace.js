import { ref } from 'vue'

export const currentNovel = ref(null)
export const activeTab = ref('import')
export const selectedSceneId = ref(null)

export function setCurrentNovel(novel) {
  currentNovel.value = novel
}

export function clearCurrentNovel() {
  currentNovel.value = null
  selectedSceneId.value = null
}

export function setActiveTab(tabName) {
  activeTab.value = tabName
}

export function openScriptEditor(sceneId) {
  selectedSceneId.value = sceneId
  activeTab.value = 'scripts'
}
