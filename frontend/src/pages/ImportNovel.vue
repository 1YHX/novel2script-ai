<template>
  <section class="import-page">
    <div class="import-form">
      <el-form label-position="top">
        <el-form-item label="项目标题">
          <el-input v-model="title" maxlength="80" placeholder="请输入剧本改编项目标题" />
        </el-form-item>

        <el-form-item label="小说正文">
          <el-input
            v-model="content"
            type="textarea"
            :rows="14"
            placeholder="粘贴小说正文，或上传 .txt 文件"
          />
        </el-form-item>

        <div class="actions">
          <el-upload
            accept=".txt"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleFileChange"
          >
            <el-button>上传 TXT</el-button>
          </el-upload>
          <el-button @click="loadExample">加载示例小说</el-button>
          <el-button type="primary" :loading="loading" @click="submitImport">开始解析</el-button>
        </div>
      </el-form>
    </div>

    <aside class="result-panel">
      <div v-if="!result" class="empty-result">
        解析结果会显示章节数、段落数和章节预览
      </div>
      <div v-else>
        <div class="result-summary">
          <strong>{{ result.title }}</strong>
          <span>{{ result.chapter_count }} 章</span>
          <span>{{ result.paragraph_count }} 段</span>
        </div>

        <el-scrollbar height="360px">
          <div v-for="chapter in result.chapters" :key="chapter.chapter_id" class="chapter-preview">
            <h3>{{ chapter.title }}</h3>
            <p v-for="paragraph in chapter.paragraphs.slice(0, 2)" :key="paragraph.paragraph_id">
              {{ paragraph.content }}
            </p>
          </div>
        </el-scrollbar>
      </div>
    </aside>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

import { importNovel } from '../api'
import { setCurrentNovel } from '../store/workspace'

const title = ref('示例小说')
const content = ref('')
const loading = ref(false)
const result = ref(null)

const exampleText = `第一章 雨夜

雨水拍在旧出租屋的窗上。林川坐在电脑前，反复查看父亲失踪前留下的最后一封邮件。

手机忽然响起，屏幕上显示的是陌生号码。电话那头的苏晚声音低而急：“你父亲不是失踪，他是在躲人。”

林川没有立刻回答。他看向桌上那张泛黄的合照，照片背面写着一个地址：城西旧仓库。

第二章 旧仓库

林川和苏晚在深夜赶到城西。仓库门口的锁已经被人撬开，里面残留着刚熄灭不久的烟味。

苏晚提醒林川不要冲动，但林川发现父亲常用的怀表被放在地上，表针停在凌晨两点十七分。

黑暗里传来脚步声。一个戴帽子的男人低声说：“想知道真相，就别相信你身边的人。”`

function loadExample() {
  title.value = '雨夜旧仓库'
  content.value = exampleText
  result.value = null
}

async function handleFileChange(file) {
  const rawFile = file.raw
  if (!rawFile) return

  if (!rawFile.name.endsWith('.txt')) {
    ElMessage.error('请上传 .txt 文件')
    return
  }

  try {
    const buffer = await rawFile.arrayBuffer()
    content.value = decodeTextFile(buffer)
    if (!title.value.trim()) {
      title.value = rawFile.name.replace(/\.txt$/i, '')
    }
    result.value = null
  } catch (error) {
    ElMessage.error('文件读取失败，请检查 txt 文件编码')
  }
}

function decodeTextFile(buffer) {
  const encodings = ['utf-8', 'gb18030', 'gbk']

  for (const encoding of encodings) {
    try {
      return new TextDecoder(encoding, { fatal: true }).decode(buffer).replace(/^\uFEFF/, '')
    } catch (error) {
      // Try the next common Chinese txt encoding.
    }
  }

  return new TextDecoder('utf-8').decode(buffer).replace(/^\uFEFF/, '')
}

async function submitImport() {
  if (!title.value.trim()) {
    ElMessage.error('请输入项目标题')
    return
  }
  if (!content.value.trim()) {
    ElMessage.error('请粘贴或上传小说正文')
    return
  }

  loading.value = true
  try {
    const response = await importNovel({
      title: title.value,
      content: content.value
    })
    result.value = response.data
    setCurrentNovel(response.data)
    ElMessage.success('小说解析完成')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '小说解析失败')
  } finally {
    loading.value = false
  }
}
</script>
