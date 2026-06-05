<template>
  <LoginPage v-if="!currentUser" />
  <main v-else class="app-shell">
    <section class="workspace">
      <div class="hero">
        <p class="eyebrow">结构化小说转剧本工作台</p>
        <h1>Novel2Script AI</h1>
        <p class="subtitle">
          将小说改编拆解为人物档案、分场大纲、单场剧本和结构化 YAML 导出。
        </p>
        <el-button class="logout-button" size="small" @click="clearCurrentUser">退出</el-button>
      </div>

      <el-tabs v-model="activeTab" class="workspace-tabs">
        <el-tab-pane label="小说导入" name="import">
          <ImportNovel />
        </el-tab-pane>
        <el-tab-pane label="人物档案" name="characters">
          <CharacterBoard />
        </el-tab-pane>
        <el-tab-pane label="分场大纲" name="scenes">
          <SceneBoard />
        </el-tab-pane>
        <el-tab-pane label="剧本编辑" name="scripts">
          <ScriptEditor />
        </el-tab-pane>
        <el-tab-pane label="导出结果" name="export">
          <ExportPanel />
        </el-tab-pane>
      </el-tabs>
    </section>
  </main>
</template>

<script setup>
import LoginPage from './pages/LoginPage.vue'
import ImportNovel from './pages/ImportNovel.vue'
import CharacterBoard from './pages/CharacterBoard.vue'
import SceneBoard from './pages/SceneBoard.vue'
import ScriptEditor from './pages/ScriptEditor.vue'
import ExportPanel from './pages/ExportPanel.vue'
import { activeTab, clearCurrentUser, currentUser } from './store/workspace'
</script>
