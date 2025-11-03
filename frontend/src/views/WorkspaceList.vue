<template>
  <div class="workspace-list">
    <n-layout>
      <n-layout-header class="header" bordered>
        <div class="header-content">
          <h1 class="logo">
            <span class="logo-icon">📖</span>
            Novel Studio
          </h1>
          <n-button type="primary" size="large" @click="showCreateModal = true" class="create-btn">
            <template #icon>
              <span>✨</span>
            </template>
            创建新小说
          </n-button>
        </div>
      </n-layout-header>

      <n-layout-content class="content">
        <!-- 搜索和过滤栏 -->
        <div v-if="store.workspaces.length > 0" class="toolbar">
          <n-input
            v-model:value="searchQuery"
            placeholder="搜索小说标题、类型或标签..."
            clearable
            class="search-input"
          >
            <template #prefix>
              <span>🔍</span>
            </template>
          </n-input>
          
          <n-space>
            <n-select
              v-model:value="sortBy"
              :options="sortOptions"
              class="sort-select"
              placeholder="排序方式"
            />
            <n-tag :bordered="false" class="count-tag">
              共 {{ filteredWorkspaces.length }} 部小说
            </n-tag>
          </n-space>
        </div>

        <n-spin :show="store.loading">
          <n-empty 
            v-if="!store.workspaces.length && !store.loading" 
            description="还没有小说，创建一个开始吧"
            class="empty-state"
          >
            <template #icon>
              <span class="empty-icon">📚</span>
            </template>
            <template #extra>
              <n-button type="primary" size="large" @click="showCreateModal = true">
                立即创建
              </n-button>
            </template>
          </n-empty>
          
          <n-empty
            v-else-if="filteredWorkspaces.length === 0"
            description="没有找到匹配的小说"
            class="empty-state"
          >
            <template #icon>
              <span class="empty-icon">🔍</span>
            </template>
          </n-empty>
          
          <transition-group v-else name="card-list" tag="div">
            <n-grid :cols="gridCols" :x-gap="24" :y-gap="24" responsive="screen">
              <n-grid-item 
                v-for="workspace in filteredWorkspaces" 
                :key="workspace.id"
                class="card-item"
              >
              <n-card 
                class="workspace-card" 
                :class="{ 'card-clicking': clickingId === workspace.id }"
                hoverable 
                @click="openWorkspace(workspace.id)"
              >
                  <template #header>
                    <div class="card-header">
                      <h3 class="card-title">{{ workspace.title }}</h3>
                      <n-tag v-if="workspace.genre" class="genre-tag" round>
                        {{ workspace.genre }}
                      </n-tag>
                    </div>
                  </template>
                  
                  <div class="card-body">
                    <div class="card-description">
                      <n-ellipsis :line-clamp="3">
                        {{ workspace.description || '暂无简介' }}
                      </n-ellipsis>
                    </div>
                    
                    <div class="card-meta">
                      <n-space size="small">
                        <span class="meta-item" :title="formatDate(workspace.updated_at)">
                          🕒 {{ formatRelativeTime(workspace.updated_at) }}
                        </span>
                        <span class="meta-item" v-if="workspace.chapter_count !== undefined">
                          📝 {{ workspace.chapter_count }} 章
                        </span>
                      </n-space>
                    </div>
                  </div>
                  
                  <template #footer>
                    <div class="card-footer">
                      <n-space size="small" class="tags">
                        <n-tag 
                          v-for="tag in getDisplayTags(workspace.tags)" 
                          :key="tag" 
                          size="small"
                          :bordered="false"
                        >
                          {{ tag }}
                        </n-tag>
                        <n-tag 
                          v-if="workspace.tags.length > 3"
                          size="small"
                          :bordered="false"
                          class="more-tag"
                        >
                          +{{ workspace.tags.length - 3 }}
                        </n-tag>
                      </n-space>
                      <n-button 
                        size="small" 
                        text 
                        type="error" 
                        @click.stop="handleDelete(workspace.id)"
                        class="delete-btn"
                      >
                        <template #icon>
                          <span>🗑️</span>
                        </template>
                      </n-button>
                    </div>
                  </template>
                </n-card>
              </n-grid-item>
            </n-grid>
          </transition-group>
        </n-spin>
      </n-layout-content>
    </n-layout>

    <!-- 创建工作区对话框 -->
    <n-modal 
      v-model:show="showCreateModal" 
      preset="card" 
      title="创建新小说"
      class="create-modal"
      :style="{ maxWidth: '600px' }"
    >
      <n-form 
        ref="formRef" 
        :model="formData" 
        :rules="formRules"
        label-placement="top"
        require-mark-placement="left"
      >
        <n-form-item label="小说标题" path="title">
          <n-input 
            v-model:value="formData.title" 
            placeholder="给你的小说起个响亮的名字"
            maxlength="50"
            show-count
          />
        </n-form-item>
        
        <n-form-item label="类型" path="genre">
          <n-input 
            v-model:value="formData.genre" 
            placeholder="如：玄幻、都市、科幻、言情"
            maxlength="20"
          />
        </n-form-item>
        
        <n-form-item label="简介" path="description">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            placeholder="简单介绍一下你的小说世界观和主要剧情"
            :rows="5"
            maxlength="500"
            show-count
          />
        </n-form-item>
        
        <n-form-item label="标签" path="tags">
          <n-dynamic-tags v-model:value="formData.tags" :max="10" />
        </n-form-item>
      </n-form>
      
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="handleCreate" :loading="creating">
            创建
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import {
  NLayout, NLayoutHeader, NLayoutContent,
  NButton, NCard, NGrid, NGridItem, NTag, NEllipsis,
  NSpin, NEmpty, NModal, NForm, NFormItem, NInput, NSpace, NDynamicTags,
  NSelect
} from 'naive-ui'
import { useWorkspaceStore } from '../stores/workspace'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const store = useWorkspaceStore()

const showCreateModal = ref(false)
const creating = ref(false)
const searchQuery = ref('')
const sortBy = ref('updated_desc')
const clickingId = ref(null)

const formData = ref({
  title: '',
  genre: '',
  description: '',
  tags: []
})

const formRef = ref(null)

// 表单验证规则 - 这才是正确的做法
const formRules = {
  title: [
    { required: true, message: '请输入小说标题', trigger: 'blur' },
    { min: 2, max: 50, message: '标题长度应在 2-50 个字符之间', trigger: 'blur' }
  ]
}

// 排序选项
const sortOptions = [
  { label: '最近更新', value: 'updated_desc' },
  { label: '最早更新', value: 'updated_asc' },
  { label: '标题 A-Z', value: 'title_asc' },
  { label: '标题 Z-A', value: 'title_desc' }
]

// 响应式网格列数 - 不要写死
const gridCols = computed(() => {
  return 'xs:1 s:1 m:2 l:3 xl:3 2xl:4'
})

// 过滤和排序 - 用计算属性，别每次渲染都算
const filteredWorkspaces = computed(() => {
  let result = [...store.workspaces]
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(w => 
      w.title.toLowerCase().includes(query) ||
      w.genre?.toLowerCase().includes(query) ||
      w.description?.toLowerCase().includes(query) ||
      w.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }
  
  // 排序
  switch (sortBy.value) {
    case 'updated_desc':
      result.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
      break
    case 'updated_asc':
      result.sort((a, b) => new Date(a.updated_at) - new Date(b.updated_at))
      break
    case 'title_asc':
      result.sort((a, b) => a.title.localeCompare(b.title, 'zh-CN'))
      break
    case 'title_desc':
      result.sort((a, b) => b.title.localeCompare(a.title, 'zh-CN'))
      break
  }
  
  return result
})

// 预处理标签显示 - 避免每次渲染都 slice
function getDisplayTags(tags) {
  return tags.slice(0, 3)
}

// 格式化日期
function formatDate(dateStr) {
  if (!dateStr) return '未知'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 相对时间显示 - 更人性化
function formatRelativeTime(dateStr) {
  if (!dateStr) return '未知'
  
  const now = new Date()
  const date = new Date(dateStr)
  const diff = now - date
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`
  if (days < 365) return `${Math.floor(days / 30)}个月前`
  return `${Math.floor(days / 365)}年前`
}

onMounted(async () => {
  try {
    await store.loadWorkspaces()
  } catch (error) {
    message.error('加载失败: ' + error.message)
  }
})

function openWorkspace(id) {
  clickingId.value = id
  // 短暂延迟让动画完成
  setTimeout(() => {
    router.push(`/workspace/${id}`)
  }, 150)
}

async function handleCreate() {
  // 用正经的表单验证，别写 if 判断
  formRef.value?.validate(async (errors) => {
    if (errors) {
      return
    }
    
    creating.value = true
    try {
      const workspace = await store.createWorkspace(formData.value)
      message.success('创建成功')
      showCreateModal.value = false
      formData.value = { title: '', genre: '', description: '', tags: [] }
      router.push(`/workspace/${workspace.id}`)
    } catch (error) {
      message.error('创建失败: ' + error.message)
    } finally {
      creating.value = false
    }
  })
}

function handleDelete(id) {
  dialog.warning({
    title: '确认删除',
    content: '删除后无法恢复，确定要删除这部小说吗？',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await store.deleteWorkspace(id)
        message.success('删除成功')
      } catch (error) {
        message.error('删除失败: ' + error.message)
      }
    }
  })
}
</script>

<style scoped>
.workspace-list {
  width: 100%;
  height: 100vh;
  background: #101014;
  overflow: hidden;
}

.header {
  height: 64px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.header-content {
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 20px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  user-select: none;
}

.logo-icon {
  font-size: 24px;
}

.create-btn {
  font-weight: 500;
}

.content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  height: calc(100vh - 64px);
  overflow-y: auto;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding: 12px 0;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

.sort-select {
  width: 140px;
}

.count-tag {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.6);
}

/* 空状态 */
.empty-state {
  margin-top: 80px;
}

.empty-icon {
  font-size: 48px;
}

/* 卡片样式 */
.workspace-card {
  height: 100%;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
}

.workspace-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.12);
}

.workspace-card.card-clicking {
  transform: scale(0.98);
  opacity: 0.7;
  transition: all 0.15s ease;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.genre-tag {
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-description {
  min-height: 60px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.6;
  font-size: 14px;
}

.card-meta {
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}

.meta-item {
  color: rgba(255, 255, 255, 0.45);
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.tags {
  flex: 1;
  overflow: hidden;
}

.more-tag {
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.45);
}

.delete-btn {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s;
}

.workspace-card:hover .delete-btn {
  opacity: 0.6;
}

.delete-btn:hover {
  opacity: 1 !important;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }
  
  .logo {
    font-size: 18px;
  }
  
  .content {
    padding: 16px;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    max-width: none;
  }
  
  .sort-select {
    width: 100%;
  }
}

/* 滚动条 */
.content::-webkit-scrollbar {
  width: 6px;
}

.content::-webkit-scrollbar-track {
  background: transparent;
}

.content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
}

.content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.12);
}
</style>

