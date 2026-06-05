import { ref } from 'vue'

const savedSession = JSON.parse(localStorage.getItem('novel2script_session') || 'null')
const savedNovel = JSON.parse(localStorage.getItem('novel2script_current_novel') || 'null')

export const currentUser = ref(savedSession)
export const currentNovel = ref(savedNovel)
export const activeTab = ref('import')
export const selectedSceneId = ref(null)

export function setCurrentUser(user) {
  currentUser.value = user
  localStorage.setItem('novel2script_session', JSON.stringify(user))
}

export function clearCurrentUser() {
  currentUser.value = null
  currentNovel.value = null
  selectedSceneId.value = null
  localStorage.removeItem('novel2script_session')
  localStorage.removeItem('novel2script_current_novel')
}

export function setCurrentNovel(novel) {
  currentNovel.value = novel
  localStorage.setItem('novel2script_current_novel', JSON.stringify(novel))
}

export function clearCurrentNovel() {
  currentNovel.value = null
  selectedSceneId.value = null
  localStorage.removeItem('novel2script_current_novel')
}

export function setActiveTab(tabName) {
  activeTab.value = tabName
}

export function openScriptEditor(sceneId) {
  selectedSceneId.value = sceneId
  activeTab.value = 'scripts'
}
