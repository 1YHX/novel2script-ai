<template>
  <article class="scene-card">
    <div class="scene-header">
      <span>第 {{ index + 1 }} 场</span>
      <h3>{{ scene.title }}</h3>
    </div>
    <dl>
      <div>
        <dt>时间</dt>
        <dd>{{ scene.time }}</dd>
      </div>
      <div>
        <dt>地点</dt>
        <dd>{{ scene.location }}</dd>
      </div>
      <div>
        <dt>人物</dt>
        <dd>{{ scene.characters.join('、') || '未知' }}</dd>
      </div>
      <div>
        <dt>剧情目的</dt>
        <dd>{{ scene.plot_goal }}</dd>
      </div>
      <div>
        <dt>冲突点</dt>
        <dd>{{ scene.conflict }}</dd>
      </div>
      <div>
        <dt>原文段落</dt>
        <dd>{{ sourceParagraphSummary }}</dd>
      </div>
    </dl>
    <el-button type="primary" plain :loading="generating" @click="$emit('generate', scene)">
      {{ generating ? '生成中' : '生成剧本' }}
    </el-button>
    <div v-if="script" class="scene-script-preview">
      <div class="scene-script-preview-header">
        <strong>已生成剧本 v{{ script.version }}</strong>
        <el-button size="small" text type="primary" @click="$emit('open-script', scene)">打开编辑</el-button>
      </div>
      <pre>{{ script.content }}</pre>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  scene: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  },
  generating: {
    type: Boolean,
    default: false
  },
  script: {
    type: Object,
    default: null
  }
})

defineEmits(['generate', 'open-script'])

const sourceParagraphSummary = computed(() => {
  const ids = props.scene.source_paragraphs || []
  if (ids.length === 0) return '未知'
  if (ids.length <= 6) return ids.join('、')

  const sorted = [...ids].sort((a, b) => a - b)
  return `${sorted[0]}-${sorted[sorted.length - 1]}（${sorted.length} 段）`
})
</script>
