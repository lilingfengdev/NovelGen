<template>
  <div class="editor-container">
    <!-- 编辑器工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <n-button 
          v-if="!chapter.plan" 
          type="primary"
          size="small"
          :loading="loading"
          :disabled="loading"
          @click="$emit('plan')"
        >
          生成大纲
        </n-button>
        <n-button 
          v-else-if="!chapter.content" 
          type="primary"
          size="small"
          :loading="loading"
          :disabled="loading"
          @click="$emit('generate')"
        >
          生成内容
        </n-button>
        <n-button 
          v-else-if="chapter.verification_passed !== 1" 
          type="warning"
          size="small"
          :loading="loading"
          :disabled="loading"
          @click="$emit('verify')"
        >
          验证内容
        </n-button>
        <n-button 
          v-else 
          type="success"
          size="small"
          :loading="loading"
          :disabled="loading"
          @click="$emit('finalize')"
        >
          确认完成
        </n-button>
        
        <n-button 
          v-if="chapter.verification_passed === -1" 
          size="small"
          :loading="loading"
          :disabled="loading"
          @click="$emit('improve')"
        >
          改进内容
        </n-button>
        
        <n-button 
          v-if="chapter.content" 
          text
          size="small"
          :loading="loading"
          :disabled="loading"
          @click="$emit('generate')"
        >
          重新生成
        </n-button>
        
        <n-button 
          v-if="chapter.plan" 
          text
          size="small"
          :loading="loading"
          :disabled="loading"
          @click="$emit('plan')"
        >
          修改大纲
        </n-button>
      </div>
      
      <div class="toolbar-right">
        <span class="status-indicator" :class="'status-' + chapter.status">
          {{ statusText(chapter.status) }}
        </span>
      </div>
    </div>

    <!-- 编辑器内容区域 -->
    <div class="editor-content">
      <!-- 大纲面板 - 结构化显示 -->
      <div v-if="chapter.plan" class="editor-panel">
        <div class="panel-header">
          <span class="panel-title">OUTLINE</span>
        </div>
        <div class="panel-content">
          <!-- 如果有结构化数据，用卡片显示 -->
          <div v-if="chapter.plan_data" class="plan-structured">
            <div class="plan-section" v-if="chapter.plan_data.title">
              <div class="plan-label">标题</div>
              <div class="plan-value plan-title">{{ chapter.plan_data.title }}</div>
            </div>
            
            <div class="plan-section" v-if="chapter.plan_data.plot_points?.length">
              <div class="plan-label">主要情节点</div>
              <ol class="plan-list">
                <li v-for="(point, idx) in chapter.plan_data.plot_points" :key="idx">{{ point }}</li>
              </ol>
            </div>
            
            <div class="plan-section" v-if="chapter.plan_data.characters?.length">
              <div class="plan-label">涉及角色</div>
              <div class="plan-tags">
                <span v-for="char in chapter.plan_data.characters" :key="char" class="plan-tag">{{ char }}</span>
              </div>
            </div>
            
            <div class="plan-section" v-if="chapter.plan_data.direction">
              <div class="plan-label">情节推进方向</div>
              <div class="plan-value">{{ chapter.plan_data.direction }}</div>
            </div>
            
            <div class="plan-section" v-if="chapter.plan_data.scenes?.length">
              <div class="plan-label">重要场景</div>
              <ol class="plan-list">
                <li v-for="(scene, idx) in chapter.plan_data.scenes" :key="idx">{{ scene }}</li>
              </ol>
            </div>
          </div>
          
          <!-- 如果没有结构化数据，显示纯文本 -->
          <n-input
            v-else
            v-model:value="chapter.plan"
            type="textarea"
            :rows="8"
            readonly
            class="editor-textarea outline-textarea"
          />
        </div>
      </div>

      <!-- 验证结果面板 -->
      <div v-if="chapter.verification_result" class="editor-panel verification-panel"
           :class="chapter.verification_passed === 1 ? 'verification-success' : 'verification-warning'">
        <div class="panel-header">
          <span class="panel-title">
            {{ chapter.verification_passed === 1 ? 'VERIFICATION PASSED' : 'VERIFICATION ISSUES' }}
          </span>
        </div>
        <div class="panel-content">
          <div v-if="chapter.verification_result.issues?.length" class="verification-section">
            <div class="verification-label">Issues:</div>
            <ul class="verification-list">
              <li v-for="(issue, i) in chapter.verification_result.issues" :key="i">
                {{ issue }}
              </li>
            </ul>
          </div>
          
          <div v-if="chapter.verification_result.suggestions?.length" class="verification-section">
            <div class="verification-label">Suggestions:</div>
            <ul class="verification-list">
              <li v-for="(sug, i) in chapter.verification_result.suggestions" :key="i">
                {{ sug }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 内容面板 -->
      <div v-if="chapter.content" class="editor-panel">
        <div class="panel-header">
          <span class="panel-title">CONTENT</span>
          <span class="panel-info">
            {{ (chapter.content || '').length.toLocaleString() }} 字符
          </span>
        </div>
        <div class="panel-content">
          <n-input
            v-model:value="chapter.content"
            type="textarea"
            :rows="25"
            readonly
            class="editor-textarea content-textarea"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { NCard, NInput, NAlert, NText, NButton, NTag, NSpace } from 'naive-ui'

const props = defineProps({
  chapter: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
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
.editor-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.2s ease-out;
}

/* 编辑器工具栏 - VSCode风格 */
.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 42px;
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.toolbar-left {
  display: flex;
  gap: 8px;
  align-items: center;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-indicator {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  padding: 4px 10px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.05);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.status-indicator.status-completed {
  color: rgba(99, 226, 183, 0.9);
  background: rgba(99, 226, 183, 0.12);
}

.status-indicator.status-generating,
.status-indicator.status-verifying,
.status-indicator.status-improving {
  color: rgba(240, 186, 82, 0.9);
  background: rgba(240, 186, 82, 0.12);
}

.status-indicator.status-failed {
  color: rgba(242, 99, 123, 0.9);
  background: rgba(242, 99, 123, 0.12);
}

/* 编辑器内容区域 */
.editor-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

/* 编辑器面板 */
.editor-panel {
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 35px;
  padding: 0 20px;
  background: rgba(255, 255, 255, 0.015);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.panel-title {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.45);
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

.panel-info {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
}

.panel-content {
  padding: 16px 20px;
}

/* Textarea样式 */
.editor-textarea {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.8;
}

.editor-textarea :deep(.n-input__textarea-el) {
  background: transparent !important;
  color: rgba(255, 255, 255, 0.85);
  border: none;
  padding: 0;
}

.content-textarea {
  font-family: 'Georgia', 'Source Han Serif SC', 'Songti SC', serif;
  font-size: 14px;
  line-height: 2;
}

.content-textarea :deep(.n-input__textarea-el) {
  color: rgba(255, 255, 255, 0.9);
}

/* 验证面板 */
.verification-panel {
  background: rgba(240, 186, 82, 0.03);
}

.verification-panel.verification-success {
  background: rgba(99, 226, 183, 0.03);
}

.verification-panel.verification-success .panel-header {
  background: rgba(99, 226, 183, 0.08);
  border-bottom-color: rgba(99, 226, 183, 0.15);
}

.verification-panel.verification-warning .panel-header {
  background: rgba(240, 186, 82, 0.08);
  border-bottom-color: rgba(240, 186, 82, 0.15);
}

.verification-section {
  margin-bottom: 16px;
}

.verification-section:last-child {
  margin-bottom: 0;
}

.verification-label {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.verification-list {
  margin: 0;
  padding-left: 20px;
  list-style: none;
}

.verification-list li {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
  line-height: 1.7;
  margin-bottom: 6px;
  position: relative;
}

.verification-list li::before {
  content: '•';
  position: absolute;
  left: -15px;
  color: rgba(255, 255, 255, 0.4);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 结构化大纲显示 */
.plan-structured {
  padding: 0;
}

.plan-section {
  margin-bottom: 24px;
}

.plan-section:last-child {
  margin-bottom: 0;
}

.plan-label {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.45);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 8px;
}

.plan-value {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.7;
}

.plan-title {
  font-size: 18px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
}

.plan-list {
  margin: 0;
  padding-left: 20px;
  list-style: decimal;
}

.plan-list li {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.8;
  margin-bottom: 10px;
}

.plan-list li:last-child {
  margin-bottom: 0;
}

.plan-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.plan-tag {
  display: inline-block;
  padding: 5px 12px;
  background: rgba(102, 126, 234, 0.12);
  border: 1px solid rgba(102, 126, 234, 0.25);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}
</style>
