<template>
  <LoginPage v-if="!currentUser" />
  <main v-else class="app-shell">
    <aside class="app-sidebar">
      <div class="brand-block">
        <p class="eyebrow">结构化小说转剧本工作台</p>
        <h1>Novel2Script AI</h1>
      </div>

      <div class="current-project">
        <span>当前项目</span>
        <strong>{{ currentNovel?.title || '未选择项目' }}</strong>
      </div>

      <nav class="side-nav">
        <button
          v-for="item in navItems"
          :key="item.name"
          :class="{ active: activeTab === item.name }"
          @click="setActiveTab(item.name)"
        >
          <span>{{ item.index }}</span>
          <strong>{{ item.label }}</strong>
          <small>{{ item.desc }}</small>
        </button>
      </nav>
    </aside>

    <section class="app-main">
      <header class="main-header">
        <div>
          <p class="eyebrow">{{ activeNav?.label }}</p>
          <h2>{{ activeNav?.title }}</h2>
        </div>
        <div class="header-meta">
          <p>{{ activeNav?.desc }}</p>
          <div class="account-bar">
            <span class="account-avatar">{{ currentUser.username.slice(0, 1).toUpperCase() }}</span>
            <span class="account-name">{{ currentUser.username }}</span>
            <el-button size="small" @click="clearCurrentUser">退出登录</el-button>
          </div>
        </div>
      </header>

      <div class="workspace-panel">
        <ImportNovel v-if="activeTab === 'import'" />
        <CharacterBoard v-else-if="activeTab === 'characters'" />
        <SceneBoard v-else-if="activeTab === 'scenes'" />
        <ScriptEditor v-else-if="activeTab === 'scripts'" />
        <ExportPanel v-else />
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import LoginPage from './pages/LoginPage.vue'
import ImportNovel from './pages/ImportNovel.vue'
import CharacterBoard from './pages/CharacterBoard.vue'
import SceneBoard from './pages/SceneBoard.vue'
import ScriptEditor from './pages/ScriptEditor.vue'
import ExportPanel from './pages/ExportPanel.vue'
import { activeTab, clearCurrentUser, currentNovel, currentUser, setActiveTab } from './store/workspace'

const navItems = [
  { index: '01', name: 'import', label: '小说导入', title: '导入与项目记录', desc: '上传文本、恢复历史项目' },
  { index: '02', name: 'characters', label: '人物档案', title: '人物档案抽取', desc: '从原文整理角色设定' },
  { index: '03', name: 'scenes', label: '分场大纲', title: '结构化分场规划', desc: '按章节事件生成可拍分场' },
  { index: '04', name: 'scripts', label: '剧本编辑', title: '单场剧本生成与编辑', desc: '生成、批量生成和改写剧本' },
  { index: '05', name: 'export', label: '导出结果', title: 'YAML 与 Markdown 导出', desc: '交付结构化剧本初稿' }
]

const activeNav = computed(() => navItems.find((item) => item.name === activeTab.value) || navItems[0])
</script>
