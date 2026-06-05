import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 20000
})

export function getHealth() {
  return api.get('/health')
}

export function importNovel(payload) {
  return api.post('/novels/import', payload)
}

export function extractCharacters(novelId) {
  return api.post(`/characters/extract/${novelId}`)
}

export function getCharacters(novelId) {
  return api.get(`/characters/${novelId}`)
}

export function planScenes(novelId, sceneCount = 5) {
  return api.post(`/scenes/plan/${novelId}`, null, {
    params: { scene_count: sceneCount }
  })
}

export function getScenes(novelId) {
  return api.get(`/scenes/${novelId}`)
}

export function generateScript(sceneId, payload) {
  return api.post(`/scripts/generate/${sceneId}`, payload)
}

export function getScript(sceneId) {
  return api.get(`/scripts/${sceneId}`)
}

export function updateScript(scriptId, payload) {
  return api.put(`/scripts/${scriptId}`, payload)
}
