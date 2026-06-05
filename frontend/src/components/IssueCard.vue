<template>
  <article class="issue-card" :class="issue.level">
    <div class="issue-header">
      <span>{{ issue.level }}</span>
      <strong>{{ issue.type }}</strong>
    </div>
    <p><b>涉及场景：</b>{{ issue.scene_id || '未知' }}</p>
    <p><b>问题描述：</b>{{ issue.description }}</p>
    <p><b>修改建议：</b>{{ issue.suggestion }}</p>
  </article>
</template>

<script setup>
defineProps({
  issue: {
    type: Object,
    required: true
  }
})
</script>
