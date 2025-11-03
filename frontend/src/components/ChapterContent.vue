<template>
  <div class="chapter-content">
    <!-- 操作按钮栏 -->
    <div class="action-bar">
      <n-space class="action-buttons">
        <n-button 
          v-if="!chapter.plan" 
          type="primary" 
          size="large"
          @click="$emit('plan')"
        >
          🎯 生成大纲
        </n-button>
        <n-button 
          v-else-if="!chapter.content" 
          type="primary" 
          size="large"
          @click="$emit('generate')"
        >
          ✨ 生成内容
        </n-button>
        <n-button 
          v-else-if="chapter.verification_passed !== 1" 
          type="warning" 
          size="large"
          @click="$emit('verify')"
        >
          🔍 验证内容
        </n-button>
        <n-button 
          v-else 
          type="success" 
          size="large"
          @click="$emit('finalize')"
        >
          ✓ 确认完成
        </n-button>
        
        <n-button 
          v-if="chapter.verification_passed === -1" 
          type="error" 
          ghost
          @click="$emit('improve')"
        >
          🔧 改进内容
        </n-button>
        
        <n-button 
          v-if="chapter.content" 
          ghost
          @click="$emit('generate')"
        >
          🔄 重新生成
        </n-button>
      </n-space>
      
      <n-tag 
        :type="statusType(chapter.status)"
        size="large"
        round
        class="status-tag"
      >
        {{ statusText(chapter.status) }}
      </n-tag>
    </div>

    <!-- 大纲区域 -->
    <n-card 
      v-if="chapter.plan"
      class="plan-card" 
      title="📋 章节大纲"
    >
      <n-input
        v-model:value="chapter.plan"
        type="textarea"
        :rows="8"
        readonly
        class="plan-textarea"
      />
    </n-card>

    <!-- 验证结果 -->
    <n-alert
      v-if="chapter.verification_result"
      :type="chapter.verification_passed === 1 ? 'success' : 'warning'"
      class="verification-alert"
    >
      <template #header>
        <strong>
          {{ chapter.verification_passed === 1 ? '✓ 验证通过' : '⚠ 需要改进' }}
        </strong>
      </template>
      
      <div v-if="chapter.verification_result.issues?.length" class="verification-section">
        <strong>问题:</strong>
        <ul class="verification-list">
          <li v-for="(issue, i) in chapter.verification_result.issues" :key="i">
            {{ issue }}
          </li>
        </ul>
      </div>
      
      <div v-if="chapter.verification_result.suggestions?.length" class="verification-section">
        <strong>建议:</strong>
        <ul class="verification-list">
          <li v-for="(sug, i) in chapter.verification_result.suggestions" :key="i">
            {{ sug }}
          </li>
        </ul>
      </div>
    </n-alert>

    <!-- 内容区域 -->
    <n-card 
      v-if="chapter.content"
      class="content-card" 
      title="📝 章节内容"
    >
      <n-input
        v-model:value="chapter.content"
        type="textarea"
        :rows="20"
        readonly
        class="content-textarea"
      />
      
      <template #footer>
        <div class="content-footer">
          <n-text depth="3">
            字数: {{ (chapter.content || '').length.toLocaleString() }}
          </n-text>
        </div>
      </template>
    </n-card>
  </div>
</template>

<script setup>
import { NCard, NInput, NAlert, NText, NButton, NTag, NSpace } from 'naive-ui'

const props = defineProps({
  chapter: {
    type: Object,
    required: true
  },
  getStatusType: {
    type: Function,
    default: null
  },
  getStatusText: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['plan', 'generate', 'verify', 'improve', 'finalize'])

function statusType(status) {
  if (props.getStatusType) return props.getStatusType(status)
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

function statusText(status) {
  if (props.getStatusText) return props.getStatusText(status)
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
</script>

<style scoped>
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
</style>
