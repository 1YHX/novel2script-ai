import { ref } from 'vue'

export const currentNovel = ref(null)

export function setCurrentNovel(novel) {
  currentNovel.value = novel
}
