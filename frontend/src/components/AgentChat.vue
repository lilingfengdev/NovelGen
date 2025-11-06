<template>
  <div class="agent-chat">
    <!-- 消息列表 -->
    <div class="messages-container" ref="messagesContainer">
      <div 
        v-for="(msg, idx) in messages" 
        :key="idx"
        :class="['message', msg.role]"
      >
        <div class="message-avatar">
          {{ msg.role === 'user' ? 'U' : 'AI' }}
        </div>
        <div class="message-content">
          <div class="message-wrapper">
            <div class="message-text">{{ msg.content }}</div>
            
            <!-- 消息操作按钮 -->
            <div class="message-actions">
              <n-button 
                v-if="msg.role === 'user' && idx === messages.length - 2"
                text 
                size="tiny"
                @click="handleRegenerate(idx)"
                :disabled="loading"
                title="重新生成"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="1 4 1 10 7 10"></polyline>
                  <polyline points="23 20 23 14 17 14"></polyline>
                  <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path>
                </svg>
              </n-button>
              <n-button 
                v-if="msg.role === 'user'"
                text 
                size="tiny"
                @click="handleEdit(idx)"
                :disabled="loading"
                title="编辑"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </n-button>
              <n-button 
                text 
                size="tiny"
                @click="handleDelete(idx)"
                :disabled="loading"
                title="删除"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </n-button>
            </div>
          </div>
          
          <!-- 工具调用显示 -->
          <div v-if="msg.tool_calls && msg.tool_calls.length" class="tool-calls">
            <div v-for="(tool, tidx) in msg.tool_calls" :key="tidx" class="tool-call">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
              </svg>
              <span class="tool-name">{{ tool.name }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 流式消息（正在生成） -->
      <div v-if="streamingMessage" class="message assistant streaming">
        <div class="message-avatar">AI</div>
        <div class="message-content">
          <div class="message-text">{{ streamingMessage }}</div>
          <span class="cursor-blink">|</span>
        </div>
      </div>
      
      <!-- 加载中 -->
      <div v-if="loading && !streamingMessage" class="message assistant">
        <div class="message-avatar">AI</div>
        <div class="message-content">
          <n-spin size="small" />
          <span class="thinking-text">思考中...</span>
        </div>
      </div>
    </div>
    
    <!-- 输入框 -->
    <div class="input-container">
      <n-input
        v-model:value="userInput"
        type="textarea"
        placeholder="描述你的想法..."
        :rows="3"
        :disabled="loading"
        @keydown.ctrl.enter="sendMessage"
        class="chat-input"
      />
      <div class="input-actions">
        <span class="input-hint">Ctrl+Enter 发送</span>
        <n-button 
          type="primary" 
          size="small"
          @click="sendMessage"
          :loading="loading"
          :disabled="!userInput.trim()"
        >
          发送
        </n-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { NInput, NButton, NSpin } from 'naive-ui'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  streamingMessage: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['send', 'edit', 'delete', 'regenerate'])

const messagesContainer = ref(null)
const userInput = ref('')

// 暴露方法供父组件调用
const setInput = (text) => {
  userInput.value = text
}

defineExpose({ setInput })

// 自动滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 监听消息变化，自动滚动
watch(() => props.messages, () => {
  scrollToBottom()
}, { deep: true })

watch(() => props.streamingMessage, () => {
  scrollToBottom()
})

// 发送消息
const sendMessage = () => {
  if (!userInput.value.trim() || props.loading) return
  
  emit('send', userInput.value)
  userInput.value = ''
}

// 编辑消息
const handleEdit = (index) => {
  emit('edit', index)
}

// 删除消息
const handleDelete = (index) => {
  emit('delete', index)
}

// 重新生成
const handleRegenerate = (index) => {
  emit('regenerate', index)
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.agent-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #101014;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  display: flex;
  gap: 10px;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-avatar {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
}

.message.user .message-avatar {
  background: rgba(102, 126, 234, 0.2);
  color: rgba(102, 126, 234, 0.95);
}

.message.assistant .message-avatar {
  background: rgba(99, 226, 183, 0.15);
  color: rgba(99, 226, 183, 0.9);
}

.message-content {
  flex: 1;
  min-width: 0;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.04);
  border-left: 2px solid rgba(255, 255, 255, 0.1);
}

.message-wrapper {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.message.user .message-content {
  border-left-color: rgba(102, 126, 234, 0.4);
}

.message.assistant .message-content {
  border-left-color: rgba(99, 226, 183, 0.4);
}

.message-text {
  flex: 1;
  font-size: 13px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.85);
  white-space: pre-wrap;
  word-break: break-word;
}

.message-actions {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s;
  flex-shrink: 0;
}

.message:hover .message-actions {
  opacity: 1;
}

.message-actions .n-button {
  padding: 2px 4px;
  color: rgba(255, 255, 255, 0.5);
  transition: all 0.15s;
}

.message-actions .n-button:hover {
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.08);
}

.message-actions svg {
  display: block;
}

.message.streaming .message-text {
  display: inline;
}

.cursor-blink {
  display: inline-block;
  width: 2px;
  height: 1em;
  background: rgba(99, 226, 183, 0.9);
  margin-left: 2px;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
}

.thinking-text {
  margin-left: 8px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
}

.tool-calls {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tool-call {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: rgba(102, 126, 234, 0.1);
  border-left: 2px solid rgba(102, 126, 234, 0.4);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.tool-call svg {
  flex-shrink: 0;
  color: rgba(102, 126, 234, 0.8);
}

.tool-name {
  font-family: 'Consolas', 'Monaco', monospace;
}

.input-container {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.02);
  flex-shrink: 0;
}

.chat-input :deep(.n-input-wrapper) {
  padding: 0;
}

.chat-input :deep(.n-input__border),
.chat-input :deep(.n-input__state-border) {
  border: none;
}

.chat-input :deep(.n-input__placeholder) {
  padding-left: 12px;
  padding-top: 8px;
}

.chat-input :deep(.n-input__textarea-el) {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  line-height: 1.6;
  padding: 8px 12px;
  border-radius: 2px;
  transition: all 0.2s;
}

.chat-input :deep(.n-input__textarea-el):focus {
  border-color: rgba(102, 126, 234, 0.5);
  background: rgba(255, 255, 255, 0.06);
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.input-hint {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}
</style>

