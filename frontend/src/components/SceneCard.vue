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
        <dd>{{ scene.source_paragraphs.join('、') || '未知' }}</dd>
      </div>
    </dl>
    <el-button type="primary" plain disabled>生成剧本</el-button>
  </article>
</template>

<script setup>
defineProps({
  scene: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  }
})
</script>
