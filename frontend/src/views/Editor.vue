<template>
  <div class="editor">
    <n-layout position="absolute">
      <!-- 头部 -->
      <n-layout-header class="editor-header" bordered>
        <div class="header-content">
          <n-button text size="large" @click="$router.push('/')" class="back-btn">
            ← 返回
          </n-button>
          <h2 class="workspace-title">{{ workspace?.title }}</h2>
        </div>
      </n-layout-header>

      <!-- 内容区域：侧边栏 + 主内容 -->
      <n-layout has-sider style="height: calc(100vh - 64px);">
        <!-- 侧边栏 - 章节列表和插件设置 -->
        <n-layout-sider
          bordered
          :width="sidebarWidth"
          :class="['chapter-sidebar', { dragging: isDragging }]"
        >
        <div class="sidebar-content">
          <n-tabs type="line" animated>
            <n-tab-pane name="chapters" tab="章节列表">
              <n-button 
                type="primary" 
                block 
                size="large"
                @click="showNewChapterModal = true"
                class="new-chapter-btn"
              >
                + 新建章节
              </n-button>
              
              <n-divider style="margin: 16px 0;" />
              
              <n-list hoverable clickable class="chapter-list">
                <n-list-item
                  v-for="chapter in chapters"
                  :key="chapter.id"
                  @click="selectChapter(chapter.id)"
                  :class="{ 'chapter-item': true, 'active': currentChapter?.id === chapter.id }"
                >
                  <template #prefix>
                    <n-tag 
                      :type="getStatusType(chapter.status)" 
                      size="small"
                      round
                      :bordered="false"
                    >
                      {{ getStatusText(chapter.status) }}
                    </n-tag>
                  </template>
                  
                  <div class="chapter-info">
                    <div class="chapter-number">第{{ chapter.chapter_number }}章</div>
                    <div class="chapter-title">{{ chapter.title || '未命名' }}</div>
                  </div>
                  
                  <template #suffix>
                    <n-dropdown 
                      :options="getChapterActions(chapter)" 
                      @select="(key) => handleChapterAction(key, chapter)"
                      placement="bottom-end"
                    >
                      <n-button text class="chapter-menu">⋮</n-button>
                    </n-dropdown>
                  </template>
                </n-list-item>
              </n-list>
            </n-tab-pane>
            
            <n-tab-pane name="plugins" tab="插件设置">
              <div class="plugins-container">
                <n-spin :show="pluginsLoading">
                  <n-empty 
                    v-if="!availablePlugins.length && !pluginsLoading"
                    description="没有可用的插件"
                    size="small"
                  />
                  
                  <div v-else class="plugin-list">
                    <div 
                      v-for="plugin in availablePlugins" 
                      :key="plugin.name"
                      class="plugin-item"
                    >
                      <n-card size="small" :bordered="false" class="plugin-card">
                        <div class="plugin-header">
                          <div class="plugin-info">
                            <div class="plugin-name">{{ plugin.name }}</div>
                            <div class="plugin-version">v{{ plugin.version }}</div>
                          </div>
                          <n-switch 
                            :value="isPluginEnabled(plugin.name)"
                            @update:value="(val) => togglePlugin(plugin.name, val)"
                            size="medium"
                          />
                        </div>
                        
                        <div class="plugin-description">
                          {{ plugin.description }}
                        </div>
                        
                        <n-collapse 
                          v-if="plugin.config_schema && isPluginEnabled(plugin.name)"
                          :default-expanded-names="[]"
                          class="plugin-config"
                        >
                          <n-collapse-item title="配置" name="config">
                            <plugin-config-form
                              :schema="plugin.config_schema"
                              :value="getPluginConfig(plugin.name)"
                              @update="(val) => updatePluginConfig(plugin.name, val)"
                            />
                          </n-collapse-item>
                        </n-collapse>
                      </n-card>
                    </div>
                  </div>
                </n-spin>
              </div>
            </n-tab-pane>
          </n-tabs>
        </div>
        <div class="sider-resizer" @mousedown="onSiderMouseDown" />
      </n-layout-sider>

      <!-- 主内容区 -->
      <n-layout-content class="main-content">
        <n-spin :show="genStore.loading">
          <n-empty 
            v-if="!currentChapter" 
            description="请选择或创建一个章节"
            class="empty-state"
          />
          
          <chapter-content
            v-else
            :chapter="currentChapter"
            :get-status-type="getStatusType"
            :get-status-text="getStatusText"
            @plan="handlePlan"
            @generate="handleGenerate"
            @verify="handleVerify"
            @improve="handleImprove"
            @finalize="handleFinalize"
          />
        </n-spin>
      </n-layout-content>
      </n-layout>
    </n-layout>

    <!-- 对话式创建章节 -->
    <n-modal 
      v-model:show="showNewChapterModal" 
      :mask-closable="false"
      :closable="!planGenerating"
      class="chapter-dialog-modal"
      style="width: 800px;"
    >
      <n-card title="创建新章节 - 对话式规划" :bordered="false">
        <n-form v-if="!planChatStarted">
          <n-form-item label="章节号">
            <n-input-number v-model:value="newChapterNumber" :min="1" style="width: 100%;" />
          </n-form-item>
          <n-form-item label="初始要求">
            <n-input
              v-model:value="newChapterInput"
              type="textarea"
              placeholder="描述你对这一章的想法（可选，也可以直接开始对话）"
              :rows="4"
            />
          </n-form-item>
          <n-space justify="end">
            <n-button @click="showNewChapterModal = false">取消</n-button>
            <n-button type="primary" @click="startPlanChat">开始规划</n-button>
          </n-space>
        </n-form>

        <div v-else class="plan-chat-container">
          <div class="messages-container">
            <div 
              v-for="(msg, idx) in planChatMessages" 
              :key="idx"
              :class="['message', msg.role]"
            >
              <div class="message-content">
                <div class="message-role">{{ msg.role === 'user' ? '你' : 'AI规划师' }}</div>
                <div class="message-text">{{ msg.content }}</div>
              </div>
            </div>
            <div v-if="planGenerating" class="message assistant">
              <div class="message-content">
                <div class="message-role">AI规划师</div>
                <div class="message-text">
                  <n-spin size="small" />
                  <span style="margin-left: 8px;">思考中...</span>
                </div>
              </div>
            </div>
          </div>

          <n-alert v-if="planCompleted" type="success" style="margin-top: 16px;">
            <template #header>大纲创建完成！</template>
            章节大纲已成功生成，你可以在编辑器中继续编辑。
          </n-alert>

          <div v-if="!planCompleted" class="input-area">
            <n-input
              v-model:value="userMessage"
              type="textarea"
              placeholder="继续和AI讨论大纲细节，或者让AI创建大纲..."
              :rows="3"
              :disabled="planGenerating"
              @keydown.ctrl.enter="sendMessage"
            />
            <n-space justify="space-between" style="margin-top: 12px;">
              <n-text depth="3" style="font-size: 12px;">Ctrl+Enter 发送</n-text>
              <n-space>
                <n-button @click="cancelPlanChat" :disabled="planGenerating">取消</n-button>
                <n-button 
                  type="primary" 
                  @click="sendMessage"
                  :loading="planGenerating"
                  :disabled="!userMessage.trim()"
                >
                  发送
                </n-button>
              </n-space>
            </n-space>
          </div>

          <n-space v-else justify="end" style="margin-top: 16px;">
            <n-button type="primary" @click="finishPlanChat">完成</n-button>
          </n-space>
        </div>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import {
  NLayout, NLayoutHeader, NLayoutSider, NLayoutContent,
  NButton, NCard, NSpace, NSpin, NEmpty, NList, NListItem,
  NTag, NDivider, NDropdown, NInput, NInputNumber,
  NModal, NForm, NFormItem, NAlert, NText, NTabs, NTabPane,
  NSwitch, NCollapse, NCollapseItem
} from 'naive-ui'
import { useWorkspaceStore } from '../stores/workspace'
import { useGenerationStore } from '../stores/generation'
import { pluginAPI } from '../services/api'
import PluginConfigForm from '../components/PluginConfigForm.vue'
import ChapterContent from '../components/ChapterContent.vue'

const route = useRoute()
const message = useMessage()
const dialog = useDialog()
const workspaceStore = useWorkspaceStore()
const genStore = useGenerationStore()

const workspaceId = computed(() => parseInt(route.params.id))
const workspace = computed(() => workspaceStore.currentWorkspace)
const chapters = computed(() => workspaceStore.chapters)
const currentChapter = computed(() => genStore.currentChapter)

const showNewChapterModal = ref(false)
const newChapterNumber = ref(1)
const newChapterInput = ref('')

// 对话式Plan状态
const planChatStarted = ref(false)
const planChatMessages = ref([])
const userMessage = ref('')
const planGenerating = ref(false)
const planCompleted = ref(false)
const currentPlanChapterId = ref(null)

// 插件相关状态
const availablePlugins = ref([])
const pluginsConfig = ref({})
const pluginsLoading = ref(false)

// 侧边栏可拉伸宽度
const SIDEBAR_MIN = 240
const SIDEBAR_MAX = 640
const sidebarWidth = ref(parseInt(localStorage.getItem('editor.sidebarWidth') || '360'))
if (Number.isNaN(sidebarWidth.value)) sidebarWidth.value = 360

const isDragging = ref(false)
let dragStartX = 0
let dragStartWidth = 0

function onSiderMouseDown(e) {
  isDragging.value = true
  dragStartX = e.clientX
  dragStartWidth = sidebarWidth.value
  window.addEventListener('mousemove', onSiderMouseMove)
  window.addEventListener('mouseup', onSiderMouseUp)
  // 防止选中文本
  document.body.style.userSelect = 'none'
}

function onSiderMouseMove(e) {
  if (!isDragging.value) return
  const delta = e.clientX - dragStartX
  let next = dragStartWidth + delta
  if (next < SIDEBAR_MIN) next = SIDEBAR_MIN
  if (next > SIDEBAR_MAX) next = SIDEBAR_MAX
  sidebarWidth.value = next
}

function onSiderMouseUp() {
  if (!isDragging.value) return
  isDragging.value = false
  window.removeEventListener('mousemove', onSiderMouseMove)
  window.removeEventListener('mouseup', onSiderMouseUp)
  document.body.style.userSelect = ''
  try {
    localStorage.setItem('editor.sidebarWidth', String(Math.round(sidebarWidth.value)))
  } catch {}
}

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', onSiderMouseMove)
  window.removeEventListener('mouseup', onSiderMouseUp)
  document.body.style.userSelect = ''
})

// 监听章节变化，更新标题
watch(currentChapter, (chapter) => {
  if (chapter && workspace.value) {
    const chapterInfo = chapter.title ? `第${chapter.chapter_number}章 ${chapter.title}` : `第${chapter.chapter_number}章`
    document.title = `${chapterInfo} - ${workspace.value.title} - Novel Studio`
  }
})

onMounted(async () => {
  try {
    await workspaceStore.loadWorkspace(workspaceId.value)
    if (chapters.value.length > 0) {
      await genStore.loadChapter(chapters.value[chapters.value.length - 1].id)
    }
    newChapterNumber.value = chapters.value.length + 1
    
    // 加载插件信息
    await loadPlugins()
    
    // 更新页面标题
    if (workspace.value?.title) {
      document.title = `${workspace.value.title} - Novel Studio`
    }
  } catch (error) {
    message.error('加载失败: ' + error.message)
  }
})

async function loadPlugins() {
  try {
    pluginsLoading.value = true
    
    // 获取所有插件
    availablePlugins.value = await pluginAPI.list()
    
    // 获取当前工作空间的插件配置
    const configData = await pluginAPI.getConfig(workspaceId.value)
    pluginsConfig.value = configData.plugins || {}
  } catch (error) {
    console.error('加载插件失败:', error)
    message.error('加载插件失败: ' + error.message)
  } finally {
    pluginsLoading.value = false
  }
}

function isPluginEnabled(pluginName) {
  return pluginsConfig.value[pluginName]?.enabled !== false
}

function getPluginConfig(pluginName) {
  return pluginsConfig.value[pluginName] || {}
}

async function togglePlugin(pluginName, enabled) {
  try {
    await pluginAPI.toggle(workspaceId.value, pluginName, enabled)
    
    if (!pluginsConfig.value[pluginName]) {
      pluginsConfig.value[pluginName] = {}
    }
    pluginsConfig.value[pluginName].enabled = enabled
    
    message.success(enabled ? '已启用插件' : '已禁用插件')
  } catch (error) {
    message.error('操作失败: ' + error.message)
  }
}

async function updatePluginConfig(pluginName, config) {
  try {
    const newConfig = {
      ...pluginsConfig.value,
      [pluginName]: {
        ...pluginsConfig.value[pluginName],
        ...config
      }
    }
    
    await pluginAPI.updateConfig(workspaceId.value, { plugins: newConfig })
    pluginsConfig.value = newConfig
    
    message.success('配置已保存')
  } catch (error) {
    message.error('保存失败: ' + error.message)
  }
}

async function selectChapter(chapterId) {
  try {
    await genStore.loadChapter(chapterId)
  } catch (error) {
    message.error('加载章节失败: ' + error.message)
  }
}

// 开始对话式规划
async function startPlanChat() {
  planChatStarted.value = true
  planChatMessages.value = []
  planCompleted.value = false
  currentPlanChapterId.value = null
  
  // 如果用户提供了初始要求，作为第一条消息
  if (newChapterInput.value.trim()) {
    planChatMessages.value.push({
      role: 'user',
      content: newChapterInput.value
    })
    await continueChat()
  } else {
    // 否则添加一个默认消息
    planChatMessages.value.push({
      role: 'user',
      content: '请帮我规划这一章的大纲'
    })
    await continueChat()
  }
}

// 发送消息
async function sendMessage() {
  if (!userMessage.value.trim() || planGenerating.value) return
  
  planChatMessages.value.push({
    role: 'user',
    content: userMessage.value
  })
  
  const msg = userMessage.value
  userMessage.value = ''
  
  await continueChat()
}

// 继续对话
async function continueChat() {
  try {
    planGenerating.value = true
    
    const result = await generationAPI.planInteractive({
      workspace_id: workspaceId.value,
      chapter_number: newChapterNumber.value,
      messages: planChatMessages.value
    })
    
    // 更新消息历史
    planChatMessages.value = result.messages
    
    // 检查是否完成
    if (result.completed && result.plan) {
      planCompleted.value = true
      currentPlanChapterId.value = result.chapter_id
      await workspaceStore.loadChapters(workspaceId.value)
      message.success('大纲创建完成！')
    }
  } catch (error) {
    message.error('对话失败: ' + error.message)
  } finally {
    planGenerating.value = false
  }
}

// 完成对话
async function finishPlanChat() {
  if (currentPlanChapterId.value) {
    await genStore.loadChapter(currentPlanChapterId.value)
  }
  resetPlanChat()
}

// 取消对话
function cancelPlanChat() {
  if (planCompleted.value) {
    finishPlanChat()
  } else {
    resetPlanChat()
  }
}

// 重置对话状态
function resetPlanChat() {
  showNewChapterModal.value = false
  planChatStarted.value = false
  planChatMessages.value = []
  userMessage.value = ''
  planGenerating.value = false
  planCompleted.value = false
  currentPlanChapterId.value = null
  newChapterInput.value = ''
  newChapterNumber.value = chapters.value.length + 1
}

// 保留旧的快速创建方法（可选）
async function handleCreateChapter() {
  try {
    await genStore.createPlan(
      workspaceId.value,
      newChapterNumber.value,
      newChapterInput.value || null
    )
    await workspaceStore.loadChapters(workspaceId.value)
    showNewChapterModal.value = false
    newChapterInput.value = ''
    newChapterNumber.value = chapters.value.length + 1
    message.success('大纲生成成功')
  } catch (error) {
    message.error('创建失败: ' + error.message)
  }
}

async function handlePlan() {
  try {
    await genStore.createPlan(workspaceId.value, currentChapter.value.chapter_number)
    message.success('大纲生成成功')
  } catch (error) {
    message.error('生成失败: ' + error.message)
  }
}

async function handleGenerate() {
  try {
    await genStore.generateContent(currentChapter.value.id)
    message.success('内容生成成功')
  } catch (error) {
    message.error('生成失败: ' + error.message)
  }
}

async function handleVerify() {
  try {
    const result = await genStore.verifyContent(currentChapter.value.id)
    if (result.passed) {
      message.success('验证通过')
    } else {
      message.warning('验证未通过，请查看问题并改进')
    }
  } catch (error) {
    message.error('验证失败: ' + error.message)
  }
}

async function handleImprove() {
  try {
    await genStore.improveContent(currentChapter.value.id)
    message.success('内容已改进，请重新验证')
  } catch (error) {
    message.error('改进失败: ' + error.message)
  }
}

async function handleFinalize() {
  try {
    await genStore.finalizeChapter(currentChapter.value.id)
    await workspaceStore.loadChapters(workspaceId.value)
    message.success('章节已完成')
  } catch (error) {
    message.error('确认失败: ' + error.message)
  }
}

function getStatusType(status) {
  const map = {
    planning: 'info',
    generating: 'warning',
    verifying: 'warning',
    improving: 'warning',
    completed: 'success',
    failed: 'error'
  }
  return map[status] || 'default'
}

function getStatusText(status) {
  const map = {
    planning: '计划中',
    generating: '生成中',
    verifying: '验证中',
    improving: '改进中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

function getChapterActions(chapter) {
  return [
    { label: '回退到此章节', key: 'rollback' },
    { label: '删除', key: 'delete' }
  ]
}

async function handleChapterAction(key, chapter) {
  if (key === 'rollback') {
    dialog.warning({
      title: '确认回退',
      content: `回退到第${chapter.chapter_number}章后，之后的章节将被删除，确定吗？`,
      positiveText: '确认',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          await workspaceStore.rollbackToChapter(workspaceId.value, chapter.id)
          message.success('回退成功')
          if (currentChapter.value?.chapter_number > chapter.chapter_number) {
            await genStore.loadChapter(chapter.id)
          }
        } catch (error) {
          message.error('回退失败: ' + error.message)
        }
      }
    })
  }
}
</script>

<style scoped>
.editor {
  width: 100%;
  height: 100vh;
  background: #101014;
}

/* 头部样式 */
.editor-header {
  height: 64px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.header-content {
  height: 100%;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-btn {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.65);
  transition: color 0.2s;
}

.back-btn:hover {
  color: rgba(255, 255, 255, 0.9);
}

.workspace-title {
  font-size: 20px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  flex: 1;
}

.header-actions {
  margin-left: auto;
}

/* 侧边栏样式 */
.chapter-sidebar {
  height: 100%;
  background: rgba(255, 255, 255, 0.02);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
}

.chapter-sidebar.dragging {
  transition: none !important;
}

.chapter-sidebar.dragging :deep(*) {
  transition: none !important;
}

.chapter-sidebar :deep(.n-tabs) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chapter-sidebar :deep(.n-tabs-pane-wrapper) {
  flex: 1;
  overflow: hidden;
}

.sidebar-content {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

/* 插件样式 */
.plugins-container {
  height: 100%;
  overflow-y: auto;
  padding: 12px 0;
}

.plugin-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.plugin-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.2s;
}

.plugin-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(102, 126, 234, 0.3);
}

.plugin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.plugin-info {
  flex: 1;
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.plugin-name {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.plugin-version {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.45);
}

.plugin-description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.65);
  line-height: 1.5;
  margin-bottom: 8px;
}

.plugin-config {
  margin-top: 12px;
  background: rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 8px;
}

.plugin-card :deep(.n-card__content) {
  padding: 14px 16px;
}

.plugin-config :deep(.n-collapse-item__header) {
  padding: 10px 14px;
  display: flex;
  align-items: center;
}

.plugin-config :deep(.n-collapse-item__header-main) {
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  line-height: 1;
}

.plugin-config :deep(.n-collapse-item-arrow) {
  font-size: 18px;
  display: flex;
  align-items: center;
}

.plugin-config :deep(.n-collapse-item__content-inner) {
  padding: 12px 14px 14px 14px;
}

.new-chapter-btn {
  font-weight: 600;
  height: 44px;
}

.chapter-list {
  background: transparent;
}

.chapter-item {
  margin-bottom: 8px;
  padding: 12px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.2s;
}

.chapter-item:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateX(2px);
}

.chapter-item.active {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.5);
}

.chapter-info {
  flex: 1;
  min-width: 0;
}

.chapter-number {
  font-weight: 600;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
}

.chapter-title {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chapter-menu {
  opacity: 0.5;
  transition: opacity 0.2s;
}

.chapter-item:hover .chapter-menu {
  opacity: 1;
}

/* 主内容区 */
.main-content {
  padding: 32px;
  height: 100%;
  overflow-y: auto;
  background: #101014;
}

/* 侧边栏分隔条 */
.sider-resizer {
  position: absolute;
  top: 0;
  right: -3px; /* 轻微覆盖主内容，方便命中 */
  width: 6px;
  height: 100%;
  cursor: col-resize;
  background: transparent;
}

.sider-resizer:hover {
  background: rgba(102, 126, 234, 0.25);
}

.empty-state {
  margin-top: 120px;
}

.chapter-content {
  max-width: 900px;
  margin: 0 auto;
  animation: fadeIn 0.3s ease-out;
}

/* 操作栏 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.action-buttons {
  flex: 1;
}

.status-tag {
  font-weight: 600;
  padding: 0 16px;
  height: 32px;
}

/* 卡片样式 */
.plan-card,
.content-card,
.verification-alert {
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
}

.plan-card :deep(.n-card__header),
.content-card :deep(.n-card__header) {
  font-size: 16px;
  font-weight: 600;
  padding: 20px 24px;
}

.plan-textarea,
.content-textarea {
  font-family: 'Consolas', 'Monaco', monospace;
  line-height: 1.8;
  font-size: 14px;
}

.content-textarea {
  font-family: 'Georgia', 'Songti SC', serif;
  font-size: 15px;
  line-height: 2;
}

.content-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

/* 验证结果样式 */
.verification-alert {
  padding: 20px;
}

.verification-section {
  margin-top: 12px;
}

.verification-section strong {
  color: rgba(255, 255, 255, 0.9);
  display: block;
  margin-bottom: 8px;
}

.verification-list {
  margin: 0;
  padding-left: 24px;
  color: rgba(255, 255, 255, 0.75);
}

.verification-list li {
  margin-bottom: 6px;
  line-height: 1.6;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 对话式Plan界面样式 */
.chapter-dialog-modal :deep(.n-card) {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.plan-chat-container {
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.messages-container {
  flex: 1;
  max-height: 500px;
  overflow-y: auto;
  padding: 16px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  margin-bottom: 16px;
}

.message {
  margin-bottom: 16px;
  animation: fadeIn 0.3s ease-out;
}

.message.user .message-content {
  margin-left: auto;
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.message.assistant .message-content {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.message-content {
  max-width: 85%;
  padding: 12px 16px;
  border-radius: 12px;
}

.message.user .message-content {
  margin-left: auto;
}

.message-role {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.85);
  white-space: pre-wrap;
  word-break: break-word;
}

.input-area {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 16px;
}

.input-area :deep(.n-input) {
  background: rgba(0, 0, 0, 0.2);
}
</style>

