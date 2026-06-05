<template>
  <main class="login-shell">
    <section class="login-panel">
      <div>
        <p class="eyebrow">Novel2Script AI</p>
        <h1>登录工作台</h1>
      </div>

      <el-form label-position="top" @submit.prevent>
        <el-form-item label="账号">
          <el-input v-model="username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" autocomplete="current-password" show-password />
        </el-form-item>
        <el-button type="primary" class="login-button" :loading="loading" @click="handleLogin">登录</el-button>
      </el-form>

      <p class="form-hint">演示账号：admin / admin123</p>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

import { login } from '../api'
import { setCurrentUser } from '../store/workspace'

const username = ref('admin')
const password = ref('admin123')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
    ElMessage.error('请输入账号和密码')
    return
  }

  loading.value = true
  try {
    const response = await login({ username: username.value, password: password.value })
    setCurrentUser(response.data)
    ElMessage.success('登录成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>
