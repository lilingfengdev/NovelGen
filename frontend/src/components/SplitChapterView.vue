<template>
  <div class="split-chapter-view">
    <!-- 左侧：内容显示 -->
    <div class="content-pane">
      <div class="content-header">
        <h3 class="content-title">
          第{{ chapter.chapter_number }}章
          <span v-if="chapter.title" class="chapter-subtitle">{{ chapter.title }}</span>
        </h3>
        <span :class="['status-badge', 'status-' + chapter.status]">
          {{ statusText }}
        </span>
      </div>
      
      <div class="content-body">
        <!-- 大纲视图 -->
        <div v-if="chapter.plan && !showFullContent" class="plan-view">
          <div v-if="chapter.plan_data" class="plan-structured">
            <div class="plan-section">
              <div class="plan-label">主要情节点</div>
              <ol class="plan-list">
                <li v-for="(point, idx) in chapter.plan_data.plot_points" :key="idx">
                  {{ point }}
                </li>
              </ol>
            </div>
            
            <div class="plan-section" v-if="chapter.plan_data.characters">
              <div class="plan-label">涉及角色</div>
              <div class="plan-tags">
                <span v-for="char in chapter.plan_data.characters" :key="char" class="plan-tag">
                  {{ char }}
                </span>
              </div>
            </div>
            
            <div class="plan-section" v-if="chapter.plan_data.direction">
              <div class="plan-label">情节推进</div>
              <div class="plan-text">{{ chapter.plan_data.direction }}</div>
            </div>
            
            <div class="plan-section" v-if="chapter.plan_data.scenes">
              <div class="plan-label">重要场景</div>
              <ol class="plan-list">
                <li v-for="(scene, idx) in chapter.plan_data.scenes" :key="idx">
                  {{ scene }}
                </li>
              </ol>
            </div>
          </div>
          <div v-else class="plan-raw">
            <pre>{{ chapter.plan }}</pre>
          </div>
        </div>
        
        <!-- 内容视图 -->
        <div v-else-if="chapterContent" class="content-view">
          <div class="content-text">
            {{ chapterContent }}
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-else class="empty-view">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <p>在右侧与 AI 对话，创建章节大纲</p>
        </div>
      </div>
      
      <!-- 内容操作栏 -->
      <div class="content-actions">
        <n-button 
          v-if="chapter.plan && !showFullContent"
          text
          size="small"
          @click="showFullContent = true"
          :disabled="!chapterContent"
        >
          查看完整内容
        </n-button>
        <n-button 
          v-if="showFullContent"
          text
          size="small"
          @click="showFullContent = false"
        >
          查看大纲
        </n-button>
      </div>
    </div>
    
    <!-- 右侧：Agent 对话 -->
    <div class="chat-pane">
      <div class="chat-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <span>Plan Agent</span>
      </div>
      
      <agent-chat 
        ref="agentChatRef"
        :messages="chatMessages"
        :loading="chatLoading"
        :streaming-message="streamingMessage"
        @send="handleSendMessage"
        @edit="handleEditMessage"
        @delete="handleDeleteMessage"
        @regenerate="handleRegenerateMessage"
      />
      
      <!-- Plan 确认按钮 -->
      <div v-if="planCreated && !planConfirmed" class="plan-confirm-bar">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>大纲已创建</span>
        <n-button size="small" type="primary" @click="confirmPlan">
          确认并生成内容
        </n-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { NButton } from 'naive-ui'
import AgentChat from './AgentChat.vue'
import { generationAPI } from '../services/api'
import { useMessage } from 'naive-ui'

const props = defineProps({
  chapter: {
    type: Object,
    required: true
  },
  workspaceId: {
    type: Number,
    required: true
  }
})

const message = useMessage()

const chatMessages = ref([])
const chatLoading = ref(false)
const streamingMessage = ref('')
const showFullContent = ref(false)
const chapterContent = ref('')
const planCreated = ref(false)
const planConfirmed = ref(false)
const currentThreadId = ref(null)
const historyLoaded = ref(false)
const agentChatRef = ref(null)

// 状态文本
const statusText = computed(() => {
  const map = {
    planning: '规划中',
    generating: '生成中',
    verifying: '验证中',
    improving: '改进中',
    completed: '已完成',
    failed: '失败'
  }
  return map[props.chapter.status] || props.chapter.status
})

// 加载聊天历史
const loadChatHistory = async () => {
  if (historyLoaded.value) return
  
  try {
    // 生成 thread_id
    const threadId = currentThreadId.value || `plan_${props.workspaceId}_${props.chapter.chapter_number}`
    
    // 从后端获取历史
    const response = await generationAPI.getPlanHistory(
      props.workspaceId,
      props.chapter.chapter_number,
      threadId
    )
    
    const localKey = `chat_history_${props.workspaceId}_${props.chapter.chapter_number}`
    
    if (response.messages && response.messages.length > 0) {
      // 过滤掉系统消息，只显示用户和助手消息
      chatMessages.value = response.messages.filter(msg => 
        msg.role === 'user' || msg.role === 'assistant'
      )
      currentThreadId.value = response.thread_id
      console.log('已恢复聊天历史:', chatMessages.value.length, '条消息')
    } else if (response.messages && response.messages.length === 0) {
      // 后端明确返回空消息，清空前端状态和缓存
      chatMessages.value = []
      currentThreadId.value = response.thread_id
      // 清空 localStorage 缓存
      try {
        localStorage.removeItem(localKey)
        console.log('后端无历史记录，已清空 localStorage 缓存')
      } catch (err) {
        console.error('清空 localStorage 失败:', err)
      }
    } else {
      // 后端返回异常或没有 messages 字段，尝试从 localStorage 恢复
      const localHistory = localStorage.getItem(localKey)
      if (localHistory) {
        try {
          const parsed = JSON.parse(localHistory)
          if (parsed.messages && Array.isArray(parsed.messages)) {
            chatMessages.value = parsed.messages
            console.log('从 localStorage 恢复了历史记录（后端异常）')
          }
        } catch (err) {
          console.error('localStorage 解析失败:', err)
        }
      }
    }
    
    historyLoaded.value = true
  } catch (error) {
    console.error('加载聊天历史失败:', error)
    // 失败时尝试从 localStorage 恢复
    const localKey = `chat_history_${props.workspaceId}_${props.chapter.chapter_number}`
    const localHistory = localStorage.getItem(localKey)
    if (localHistory) {
      try {
        const parsed = JSON.parse(localHistory)
        if (parsed.messages && Array.isArray(parsed.messages)) {
          chatMessages.value = parsed.messages
          console.log('从 localStorage 恢复了历史记录（后端失败后备份）')
        }
      } catch (err) {
        console.error('localStorage 解析失败:', err)
      }
    }
    historyLoaded.value = true
  }
}

// 保存聊天历史到 localStorage（作为备份）
const saveChatHistory = () => {
  const localKey = `chat_history_${props.workspaceId}_${props.chapter.chapter_number}`
  try {
    localStorage.setItem(localKey, JSON.stringify({
      messages: chatMessages.value,
      threadId: currentThreadId.value,
      timestamp: Date.now()
    }))
  } catch (error) {
    console.error('保存聊天历史到 localStorage 失败:', error)
  }
}

// 加载章节内容（从 Store）
const loadChapterContent = async () => {
  try {
    const response = await generationAPI.getChapterContent(
      props.chapter.id,
      props.workspaceId
    )
    chapterContent.value = response.content
  } catch (error) {
    console.error('加载章节内容失败:', error)
  }
}

// 发送消息
const handleSendMessage = async (messageText) => {
  if (!messageText.trim() || chatLoading.value) return
  
  // 添加用户消息
  chatMessages.value.push({
    role: 'user',
    content: messageText
  })
  
  // 立即保存到 localStorage
  saveChatHistory()
  
  chatLoading.value = true
  streamingMessage.value = ''
  
  try {
    // 使用 fetch stream 接收 SSE
    const response = await fetch('/api/plan/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        workspace_id: props.workspaceId,
        chapter_number: props.chapter.chapter_number,
        message: messageText,
        thread_id: currentThreadId.value || null,
        model: null
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let currentMessage = ''
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.substring(6))
            
            if (data.type === 'message_chunk') {
              currentMessage += data.content
              streamingMessage.value = currentMessage
            } else if (data.type === 'tool_start') {
              console.log('Tool started:', data.tool_name)
            } else if (data.type === 'tool_end') {
              console.log('Tool ended:', data.tool_name)
              if (data.tool_name === 'create_plan') {
                planCreated.value = true
                // 重新加载章节以获取最新的 plan 数据
                emit('reload-chapter')
              }
            } else if (data.type === 'plan_created') {
              planCreated.value = true
              // 重新加载章节以获取最新的 plan 数据
              emit('reload-chapter')
            } else if (data.type === 'done') {
              if (currentMessage) {
                chatMessages.value.push({
                  role: 'assistant',
                  content: currentMessage
                })
                // 保存到 localStorage
                saveChatHistory()
              }
              streamingMessage.value = ''
              chatLoading.value = false
            } else if (data.type === 'error') {
              message.error('对话失败: ' + data.message)
              chatLoading.value = false
              streamingMessage.value = ''
            }
          } catch (err) {
            console.error('解析事件失败:', err)
          }
        }
      }
    }
  } catch (error) {
    message.error('发送消息失败: ' + error.message)
    chatLoading.value = false
    streamingMessage.value = ''
  }
}

// 确认 Plan
const confirmPlan = async () => {
  try {
    await generationAPI.confirmPlan(props.chapter.id)
    planConfirmed.value = true
    message.success('大纲已确认！现在可以生成内容了')
    // 触发生成
    emit('generate')
  } catch (error) {
    message.error('确认失败: ' + error.message)
  }
}

// 编辑消息
const handleEditMessage = (index) => {
  if (index < chatMessages.value.length && chatMessages.value[index].role === 'user') {
    const msg = chatMessages.value[index]
    // 把消息内容填充到输入框
    if (agentChatRef.value) {
      agentChatRef.value.setInput(msg.content)
    }
    // 删除该消息及之后的所有消息
    chatMessages.value = chatMessages.value.slice(0, index)
    saveChatHistory()
    message.info('消息已填入输入框，修改后重新发送')
  }
}

// 删除消息（及之后的所有消息）
const handleDeleteMessage = (index) => {
  if (index < chatMessages.value.length) {
    chatMessages.value = chatMessages.value.slice(0, index)
    saveChatHistory()
    message.success('已删除该消息及之后的对话')
  }
}

// 重新生成（从某条用户消息开始）
const handleRegenerateMessage = async (index) => {
  if (index < chatMessages.value.length) {
    const userMessage = chatMessages.value[index]
    // 删除该消息之后的所有消息
    chatMessages.value = chatMessages.value.slice(0, index + 1)
    // 重新发送
    await handleSendMessage(userMessage.content)
  }
}

// 监听章节变化
watch(() => props.chapter, async (newChapter, oldChapter) => {
  // 章节号变化，需要重新加载历史
  if (!oldChapter || newChapter.chapter_number !== oldChapter.chapter_number) {
    historyLoaded.value = false
    chatMessages.value = []
    currentThreadId.value = null
    await loadChatHistory()
  }
  
  if (newChapter.content || newChapter.status === 'completed') {
    await loadChapterContent()
  }
  
  planCreated.value = !!newChapter.plan
  planConfirmed.value = newChapter.status !== 'planning'
}, { immediate: true })

// 监听消息变化，自动保存（防抖）
let saveTimer = null
watch(() => chatMessages.value, () => {
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    saveChatHistory()
  }, 1000)
}, { deep: true })

const emit = defineEmits(['generate', 'finalize', 'reload-chapter'])
</script>

<style scoped>
.split-chapter-view {
  height: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: rgba(255, 255, 255, 0.08);
}

.content-pane,
.chat-pane {
  background: #101014;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 内容面板 */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.content-title {
  font-size: 18px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}

.chapter-subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-weight: 400;
  margin-left: 8px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.status-planning {
  background: rgba(102, 126, 234, 0.15);
  color: rgba(102, 126, 234, 0.95);
}

.status-badge.status-generating {
  background: rgba(240, 186, 82, 0.15);
  color: rgba(240, 186, 82, 0.95);
}

.status-badge.status-completed {
  background: rgba(99, 226, 183, 0.15);
  color: rgba(99, 226, 183, 0.95);
}

.content-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.plan-view,
.content-view {
  max-width: 800px;
  margin: 0 auto;
}

.plan-structured {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.plan-section {
  
}

.plan-label {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.plan-list {
  margin: 0;
  padding-left: 20px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.8;
}

.plan-list li {
  margin-bottom: 8px;
}

.plan-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.plan-tag {
  padding: 4px 12px;
  background: rgba(102, 126, 234, 0.12);
  border: 1px solid rgba(102, 126, 234, 0.25);
  border-radius: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
}

.plan-text {
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.8;
}

.content-text {
  color: rgba(255, 255, 255, 0.9);
  line-height: 2;
  font-size: 15px;
  white-space: pre-wrap;
  font-family: 'Georgia', 'Songti SC', serif;
}

.empty-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  color: rgba(255, 255, 255, 0.3);
}

.empty-view svg {
  opacity: 0.3;
}

.empty-view p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.4);
}

.content-actions {
  padding: 12px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  gap: 8px;
}

/* 对话面板 */
.chat-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
}

.chat-header svg {
  color: rgba(99, 226, 183, 0.9);
}

/* Plan 确认栏 */
.plan-confirm-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(99, 226, 183, 0.08);
  border-top: 1px solid rgba(99, 226, 183, 0.2);
  color: rgba(99, 226, 183, 0.95);
  font-size: 13px;
}

.plan-confirm-bar svg {
  flex-shrink: 0;
}

.plan-confirm-bar span {
  flex: 1;
}
</style>

