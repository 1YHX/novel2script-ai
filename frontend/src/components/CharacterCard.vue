<template>
  <article class="character-card">
    <div class="character-header">
      <h3>{{ character.name }}</h3>
      <span>{{ character.role }}</span>
    </div>
    <p><strong>性格：</strong>{{ character.personality.join('、') }}</p>
    <p><strong>目标：</strong>{{ character.goal }}</p>
    <p><strong>首次出现：</strong>{{ character.first_appearance }}</p>
    <p>
      <strong>关系：</strong>
      <template v-if="character.relations.length">
        {{ character.relations.map((item) => `${item.target} / ${item.relation}`).join('；') }}
      </template>
      <template v-else>未知</template>
    </p>
    <p class="evidence"><strong>证据：</strong>{{ character.evidence }}</p>
  </article>
</template>

<script setup>
defineProps({
  character: {
    type: Object,
    required: true
  }
})
</script>
