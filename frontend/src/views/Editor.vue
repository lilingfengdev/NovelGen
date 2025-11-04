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

      <!-- 主布局：左侧工具栏 + 内容区 -->
      <n-layout has-sider style="height: calc(100vh - 64px);">
        <!-- 左侧垂直工具栏 -->
        <n-layout-sider
          :width="60"
          :collapsed-width="60"
          class="workspace-toolbar"
          bordered
        >
          <div class="toolbar-items">
            <n-tooltip placement="right" :delay="300">
              <template #trigger>
                <div 
                  :class="['toolbar-item', { active: activeWorkspace === 'editor' }]"
                  @click="activeWorkspace = 'editor'"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="12" y1="18" x2="12" y2="12"/>
                    <line x1="9" y1="15" x2="15" y2="15"/>
                  </svg>
                </div>
              </template>
              编辑器
            </n-tooltip>

            <n-tooltip placement="right" :delay="300">
              <template #trigger>
                <div 
                  :class="['toolbar-item', { active: activeWorkspace === 'plugins' }]"
                  @click="activeWorkspace = 'plugins'"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <path d="M7 7h.01"/>
                    <path d="M17 7h.01"/>
                    <path d="M7 17h.01"/>
                    <path d="M17 17h.01"/>
                  </svg>
                </div>
              </template>
              插件
            </n-tooltip>

            <n-tooltip placement="right" :delay="300">
              <template #trigger>
                <div 
                  :class="['toolbar-item', { active: activeWorkspace === 'settings' }]"
                  @click="activeWorkspace = 'settings'"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </div>
              </template>
              设置
            </n-tooltip>

            <!-- 插件注入：工作区Tab -->
            <n-tooltip 
              v-for="tab in pluginWorkspaceTabs" 
              :key="tab.key"
              placement="right" 
              :delay="300"
            >
              <template #trigger>
                <div 
                  :class="['toolbar-item', { active: activeWorkspace === tab.key }]"
                  @click="activeWorkspace = tab.key"
                >
                  <component :is="tab.icon" />
                </div>
              </template>
              {{ tab.tooltip || tab.label }}
            </n-tooltip>
          </div>
        </n-layout-sider>

        <!-- 编辑器工作区 -->
        <transition name="workspace-fade" mode="out-in">
        <n-layout has-sider style="height: 100%;" v-if="activeWorkspace === 'editor'" key="editor">
        <!-- 侧边栏 - 章节列表和插件设置 -->
        <n-layout-sider
          bordered
          :width="sidebarWidth"
          :class="['chapter-sidebar', { dragging: isDragging }]"
        >
        <div class="sidebar-content">
          <div class="sidebar-header">
            <span class="sidebar-title">章节</span>
              <n-button 
              text 
              size="tiny"
              @click="startPlanChat"
              class="new-chapter-icon-btn"
              >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              </n-button>
          </div>
          
          <!-- 插件注入：侧边栏章节列表前 -->
          <component 
            v-for="(item, idx) in pluginSidebarBefore" 
            :key="'sidebar-before-' + idx"
            :is="item.component"
            v-bind="item.props || {}"
          />
              
              <div class="chapter-tree">
                <transition-group name="chapter-list">
                <div
                  v-for="chapter in chapters"
                  :key="chapter.id"
                  @click="selectChapter(chapter.id)"
                  :class="['chapter-tree-item', { 'active': currentChapter?.id === chapter.id }]"
                >
                  <div class="chapter-tree-item-content">
                    <span :class="['status-dot', 'status-' + chapter.status]"></span>
                    <span class="chapter-label">
                      第{{ chapter.chapter_number }}章
                      <span v-if="chapter.title" class="chapter-subtitle">- {{ chapter.title }}</span>
                    </span>
                    <div class="chapter-actions" @click.stop>
                    <n-dropdown 
                      :options="getChapterActions(chapter)" 
                      @select="(key) => handleChapterAction(key, chapter)"
                      placement="bottom-end"
                        trigger="click"
                    >
                        <span class="chapter-more">
                          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="1"/>
                            <circle cx="12" cy="5" r="1"/>
                            <circle cx="12" cy="19" r="1"/>
                          </svg>
                        </span>
                    </n-dropdown>
                    </div>
                  </div>
                </div>
                </transition-group>
              </div>
          
          <!-- 插件注入：侧边栏章节列表后 -->
          <component 
            v-for="(item, idx) in pluginSidebarAfter" 
            :key="'sidebar-after-' + idx"
            :is="item.component"
            v-bind="item.props || {}"
          />
        </div>
        <div class="sider-resizer" @mousedown="onSiderMouseDown" />
      </n-layout-sider>
            
      <!-- 主内容区 -->
      <n-layout-content class="main-content">
        <!-- 对话式创建章节 -->
        <div v-if="planChatActive" class="plan-chat-view">
          <div class="plan-chat-header">
            <div class="header-title">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="12" y1="18" x2="12" y2="12"/>
                <line x1="9" y1="15" x2="15" y2="15"/>
              </svg>
              <span>创建新章节：第{{ newChapterNumber }}章</span>
            </div>
            <n-button text size="small" @click="cancelPlanChat" class="close-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </n-button>
          </div>

          <div class="plan-chat-messages" ref="messagesContainer">
            <div 
              v-for="(msg, idx) in planChatMessages" 
              :key="idx"
              :class="['chat-message', msg.role]"
            >
              <div class="message-avatar">{{ msg.role === 'user' ? 'U' : 'AI' }}</div>
              <div class="message-bubble">
                <div v-if="editingMessageIndex === idx" class="message-edit">
                  <n-input
                    v-model:value="editingMessageContent"
                    type="textarea"
                    :rows="3"
                    autofocus
                    class="edit-input"
                  />
                  <div class="edit-actions">
                    <n-button size="tiny" @click="cancelEditMessage">取消</n-button>
                    <n-button size="tiny" type="primary" @click="saveEditMessage(idx)">保存并重新生成</n-button>
                  </div>
                </div>
                <div v-else class="message-content-wrapper">
                  <div class="message-text">{{ msg.content }}</div>
                  <div class="message-actions">
                    <n-button 
                      v-if="msg.role === 'user' && idx === planChatMessages.length - 2"
                      text 
                      size="tiny"
                      @click="regenerateFromMessage(idx)"
                      :disabled="planGenerating"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="1 4 1 10 7 10"></polyline>
                        <polyline points="23 20 23 14 17 14"></polyline>
                        <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path>
                      </svg>
                    </n-button>
                    <n-button 
                      v-if="msg.role === 'user'"
                      text 
                      size="tiny"
                      @click="startEditMessage(idx, msg.content)"
                      :disabled="planGenerating"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                      </svg>
                    </n-button>
                    <n-button 
                      text 
                      size="tiny"
                      @click="deleteMessageFrom(idx)"
                      :disabled="planGenerating"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                    </n-button>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="planGenerating" class="chat-message assistant">
              <div class="message-avatar">AI</div>
              <div class="message-bubble">
                <n-spin size="small" />
                <span style="margin-left: 8px; color: rgba(255,255,255,0.5);">思考中...</span>
              </div>
            </div>
          </div>

          <div v-if="planCompleted" class="plan-completed-banner">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            <span>大纲已生成</span>
            <n-button size="small" type="success" @click="finishPlanChat">查看章节</n-button>
          </div>

          <div v-if="!planCompleted" class="plan-chat-input">
            <n-input
              v-model:value="userMessage"
              type="textarea"
              placeholder="描述你的想法，或直接让 AI 开始创建..."
              :rows="3"
              :disabled="planGenerating"
              @keydown.ctrl.enter="sendMessage"
              class="chat-input"
            />
            <div class="input-actions">
              <span class="input-hint">Ctrl+Enter 发送</span>
              <n-button 
                type="primary" 
                size="small"
                @click="sendMessage"
                :loading="planGenerating"
                :disabled="!userMessage.trim()"
              >
                发送
              </n-button>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <n-empty 
          v-else-if="!currentChapter" 
          description="选择章节开始编辑"
          class="empty-state"
        >
          <template #icon>
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.3;">
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </template>
        </n-empty>
        
        <!-- 章节内容 -->
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
      </n-layout-content>
        </n-layout>

        <!-- 插件管理工作区 -->
        <n-layout-content v-else-if="activeWorkspace === 'plugins'" key="plugins" class="workspace-content">
                  <n-empty 
                    v-if="!availablePlugins.length && !pluginsLoading"
                    description="没有可用的插件"
            style="height: 100%; display: flex; align-items: center; justify-content: center;"
                  />
                  
          <div v-else class="workspace-container">
            <n-tabs 
              v-model:value="activePluginTab" 
              type="line" 
              class="workspace-tabs-vertical"
              animated
              placement="left"
            >
              <n-tab-pane 
                      v-for="plugin in availablePlugins" 
                      :key="plugin.name"
                :name="plugin.name" 
                :tab="plugin.name"
                    >
                <div class="tab-content">
                  <n-spin :show="pluginsLoading">
                    <div class="plugin-detail">
                      <div class="plugin-detail-header">
                        <div class="plugin-detail-info">
                          <h2 class="plugin-detail-name">
                            {{ plugin.name }}
                            <span v-if="plugin.is_frontend" class="plugin-badge-builtin">前端</span>
                          </h2>
                          <span class="plugin-detail-version">v{{ plugin.version }}</span>
                          </div>
                          <n-switch 
                            v-if="!plugin.is_frontend"
                            :value="isPluginEnabled(plugin.name)"
                            @update:value="(val) => togglePlugin(plugin.name, val)"
                        size="large"
                          />
                          <span 
                            v-else 
                            :class="plugin.is_frontend_enabled ? 'plugin-status-builtin-enabled' : 'plugin-status-builtin-disabled'"
                          >
                            {{ plugin.is_frontend_enabled ? '已启用' : '已禁用' }}
                          </span>
                        </div>
                        
                      <div class="plugin-detail-description">
                          {{ plugin.description }}
                        </div>
                        
                      <div v-if="plugin.config_schema && isPluginEnabled(plugin.name)" class="plugin-detail-config">
                        <h3 class="config-section-title">配置选项</h3>
                            <plugin-config-form
                              :schema="plugin.config_schema"
                              :value="getPluginConfig(plugin.name)"
                              @update="(val) => updatePluginConfig(plugin.name, val)"
                            />
                    </div>
                      
                      <div v-else-if="!isPluginEnabled(plugin.name)" class="plugin-disabled-notice">
                      <n-empty 
                          v-if="plugin.is_frontend"
                          description="该前端插件已禁用"
                          style="margin-top: 40px;"
                        >
                          <template #extra>
                            <div style="color: rgba(255,255,255,0.5); font-size: 13px; line-height: 1.6; text-align: center; max-width: 400px; margin: 0 auto;">
                              在 <code style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">vite.config.js</code> 中修改配置以启用此插件
                            </div>
                          </template>
                        </n-empty>
                        <n-empty 
                          v-else
                        description="启用插件以配置选项"
                        style="margin-top: 40px;"
                      />
                      </div>
                  </div>
                </n-spin>
              </div>
              </n-tab-pane>
            </n-tabs>
        </div>
      </n-layout-content>
            
        <!-- 插件注入：自定义工作区Tab内容 -->
        <n-layout-content 
          v-else-if="pluginWorkspaceTabs.find(t => t.key === activeWorkspace)"
          :key="activeWorkspace"
          class="workspace-content"
        >
          <component 
            :is="pluginWorkspaceTabs.find(t => t.key === activeWorkspace).component"
            v-bind="pluginWorkspaceTabs.find(t => t.key === activeWorkspace).props || {}"
          />
        </n-layout-content>

        <!-- 系统设置工作区 -->
        <n-layout-content v-else-if="activeWorkspace === 'settings'" key="settings" class="workspace-content">
          <div class="workspace-container">
            <n-tabs 
              v-model:value="activeSettingsTab" 
              type="line" 
              class="workspace-tabs-vertical"
              animated
              placement="left"
            >
              <n-tab-pane name="model" tab="模型">
                <div class="tab-content">
                  <div class="settings-section">
                    <div class="settings-section-header">
              <div class="settings-actions">
                <n-button text @click="resetSystemConfig">
                  重置为默认值
                </n-button>
                <n-button type="primary" @click="saveSystemConfig" :loading="savingSystemConfig">
                  保存
                </n-button>
              </div>
            </div>

            <div class="settings-content">
              <!-- 模型选择 -->
              <div class="setting-item">
                <div class="setting-header">
                  <div class="setting-title">模型 (Model)</div>
                  <div class="setting-description">
                    指定该工作区使用的 AI 模型。留空则使用系统默认模型
                  </div>
                </div>
                <div class="setting-control">
                  <n-input 
                    v-model:value="systemConfig.model"
                    placeholder="留空使用系统默认模型"
                    clearable
                    size="medium"
                    style="width: 100%;"
                  />
                  <div class="setting-hint">
                    设置后，该工作区的所有生成操作都将使用此模型
                  </div>
                </div>
              </div>

              <n-divider class="setting-divider" />
              
              <!-- 温度设置 -->
              <div class="setting-item">
                <div class="setting-header">
                  <div class="setting-title">Temperature</div>
                  <div class="setting-description">
                    控制生成文本的随机性和创造性。较低的值（0-0.3）使输出更确定和一致，较高的值（1.5-2.0）使输出更随机和多样化。
                  </div>
                </div>
                <div class="setting-control">
                  <div class="control-row">
                    <n-slider 
                      v-model:value="systemConfig.temperature"
                      :min="0"
                      :max="2"
                      :step="0.1"
                      :marks="{0: '0', 0.7: '0.7', 1: '1', 2: '2'}"
                      style="flex: 1; margin-right: 16px;"
                    />
                    <n-input-number 
                      v-model:value="systemConfig.temperature"
                      :min="0"
                      :max="2"
                      :step="0.1"
                      size="small"
                      style="width: 100px;"
                    />
                  </div>
                  <div class="setting-hint">
                    推荐值：0.7（平衡创造性和一致性）
                  </div>
                </div>
              </div>

              <n-divider class="setting-divider" />

              <!-- 最大令牌数设置 -->
              <div class="setting-item">
                <div class="setting-header">
                  <div class="setting-title">Max Tokens</div>
                  <div class="setting-description">
                    限制单次生成的最大长度。1个令牌约等于0.75个英文单词或0.5个中文字。设置更高的值可以生成更长的内容，但会消耗更多资源和时间。留空使用模型默认值。
                  </div>
                </div>
                <div class="setting-control">
                  <n-input-number 
                    v-model:value="systemConfig.max_tokens"
                    :min="100"
                    :max="32000"
                    :step="100"
                    size="medium"
                    style="width: 200px;"
                    clearable
                  />
                  <div class="setting-hint">
                    推荐值：2000-4000（标准章节内容）
                  </div>
                </div>
              </div>

              <n-divider class="setting-divider" />

              <!-- Top P 设置 -->
              <div class="setting-item">
                <div class="setting-header">
                  <div class="setting-title">Top P (Nucleus Sampling)</div>
                  <div class="setting-description">
                    核心采样参数。控制模型从累积概率最高的token中选择。值越小输出越确定，值越大输出越多样。留空使用模型默认值。
                  </div>
                </div>
                <div class="setting-control">
                  <div class="control-row">
                    <n-slider 
                      v-model:value="systemConfig.top_p"
                      :min="0"
                      :max="1"
                      :step="0.05"
                      :marks="{0: '0', 0.5: '0.5', 0.9: '0.9', 1: '1'}"
                      style="flex: 1; margin-right: 16px;"
                    />
                    <n-input-number 
                      v-model:value="systemConfig.top_p"
                      :min="0"
                      :max="1"
                      :step="0.05"
                      size="small"
                      style="width: 100px;"
                      clearable
                    />
                  </div>
                  <div class="setting-hint">
                    推荐值：0.9-0.95（高质量生成）
                  </div>
                </div>
              </div>

              <n-divider class="setting-divider" />

              <!-- Top K 设置 -->
              <div class="setting-item">
                <div class="setting-header">
                  <div class="setting-title">Top K</div>
                  <div class="setting-description">
                    限制每次采样时考虑的候选token数量。值越小输出越集中，值越大输出可能性更多。部分模型支持。留空使用模型默认值。
                  </div>
                </div>
                <div class="setting-control">
                  <n-input-number 
                    v-model:value="systemConfig.top_k"
                    :min="1"
                    :max="100"
                    :step="1"
                    size="medium"
                    style="width: 200px;"
                    clearable
                  />
                  <div class="setting-hint">
                    推荐值：40-50
                  </div>
                </div>
              </div>

              <n-divider class="setting-divider" />

              <!-- Frequency Penalty 设置 -->
              <div class="setting-item">
                <div class="setting-header">
                  <div class="setting-title">Frequency Penalty</div>
                  <div class="setting-description">
                    频率惩罚。降低重复使用相同token的概率。正值会减少重复，负值会增加重复。范围 -2.0 到 2.0。留空使用模型默认值。
                  </div>
                </div>
                <div class="setting-control">
                  <div class="control-row">
                    <n-slider 
                      v-model:value="systemConfig.frequency_penalty"
                      :min="-2"
                      :max="2"
                      :step="0.1"
                      :marks="{'-2': '-2', 0: '0', 1: '1', 2: '2'}"
                      style="flex: 1; margin-right: 16px;"
                    />
                    <n-input-number 
                      v-model:value="systemConfig.frequency_penalty"
                      :min="-2"
                      :max="2"
                      :step="0.1"
                      size="small"
                      style="width: 100px;"
                      clearable
                    />
                  </div>
                  <div class="setting-hint">
                    推荐值：0.0-0.5（减少重复）
                  </div>
                </div>
              </div>

              <n-divider class="setting-divider" />

              <!-- Presence Penalty 设置 -->
              <div class="setting-item">
                <div class="setting-header">
                  <div class="setting-title">Presence Penalty</div>
                  <div class="setting-description">
                    存在惩罚。降低已经出现过的token再次出现的概率。正值鼓励谈论新话题，负值使模型更专注已有话题。范围 -2.0 到 2.0。留空使用模型默认值。
                  </div>
                </div>
                <div class="setting-control">
                  <div class="control-row">
                    <n-slider 
                      v-model:value="systemConfig.presence_penalty"
                      :min="-2"
                      :max="2"
                      :step="0.1"
                      :marks="{'-2': '-2', 0: '0', 1: '1', 2: '2'}"
                      style="flex: 1; margin-right: 16px;"
                    />
                    <n-input-number 
                      v-model:value="systemConfig.presence_penalty"
                      :min="-2"
                      :max="2"
                      :step="0.1"
                      size="small"
                      style="width: 100px;"
                      clearable
                    />
                  </div>
                  <div class="setting-hint">
                    推荐值：0.0-0.5（鼓励新内容）
                  </div>
                </div>
              </div>

              <n-divider class="setting-divider" />

              <!-- Logit Bias 设置 -->
              <div class="setting-item">
                <div class="setting-header">
                  <div class="setting-title">Logit Bias</div>
                  <div class="setting-description">
                    Token偏置。修改特定token的出现概率。格式为JSON对象，键是token ID（字符串），值是偏置（-100到100）。例如: {"50256": -100} 会完全禁止token 50256。留空使用模型默认值。
                  </div>
                </div>
                <div class="setting-control">
                  <n-input 
                    v-model:value="logitBiasText"
                    type="textarea"
                    placeholder='{"50256": -100, "13": 0.5}'
                    :rows="3"
                    @blur="parseLogitBias"
                    style="font-family: 'Consolas', 'Monaco', monospace; font-size: 13px;"
                  />
                  <div class="setting-hint">
                    高级功能。输入JSON格式的token偏置映射。
                  </div>
                </div>
              </div>
            </div>
                  </div>
                </div>
              </n-tab-pane>
            </n-tabs>
          </div>
        </n-layout-content>
        </transition>
      </n-layout>
    </n-layout>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, TransitionGroup } from 'vue'
import { useRoute } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import {
  NLayout, NLayoutHeader, NLayoutSider, NLayoutContent,
  NButton, NCard, NSpace, NSpin, NEmpty,
  NDropdown, NInput, NInputNumber,
  NTooltip, NSlider, NDivider,
  NSwitch, NCollapse, NCollapseItem,
  NTabs, NTabPane
} from 'naive-ui'
import { useWorkspaceStore } from '../stores/workspace'
import { useGenerationStore } from '../stores/generation'
import { pluginAPI, generationAPI, workspaceAPI } from '../services/api'
import PluginConfigForm from '../components/PluginConfigForm.vue'
import ChapterContent from '../components/ChapterContent.vue'
import { pluginManager } from '../plugins/manager'

const route = useRoute()
const message = useMessage()
const dialog = useDialog()
const workspaceStore = useWorkspaceStore()
const genStore = useGenerationStore()

const workspaceId = computed(() => parseInt(route.params.id))
const workspace = computed(() => workspaceStore.currentWorkspace)
const chapters = computed(() => workspaceStore.chapters)
const currentChapter = computed(() => genStore.currentChapter)

const newChapterNumber = ref(1)

// 工作区切换
const activeWorkspace = ref('editor')

// 二级Tab状态
const activePluginTab = ref('')
const activeSettingsTab = ref('model')

// 对话式Plan状态
const planChatActive = ref(false)
const planChatMessages = ref([])
const userMessage = ref('')
const planGenerating = ref(false)
const planCompleted = ref(false)
const currentPlanChapterId = ref(null)
const messagesContainer = ref(null)
const editingMessageIndex = ref(null)
const editingMessageContent = ref('')

// 插件相关状态
const availablePlugins = ref([])
const pluginsConfig = ref({})
const pluginsLoading = ref(false)

// 系统设置
const systemConfig = ref({
  model: null,
  temperature: 0.7,
  max_tokens: 2000,
  top_p: null,
  top_k: null,
  frequency_penalty: null,
  presence_penalty: null,
  logit_bias: null
})
const savingSystemConfig = ref(false)
const logitBiasText = ref('')  // logit_bias的JSON文本

// 插件系统
const pluginSidebarBefore = computed(() => {
  return pluginManager.callHook('sidebar.items', {
    workspace: workspace.value,
    chapters: chapters.value,
    currentChapter: currentChapter.value,
    position: 'before'
  }).map(r => r.result).filter(Boolean)
})

const pluginSidebarAfter = computed(() => {
  return pluginManager.callHook('sidebar.items', {
    workspace: workspace.value,
    chapters: chapters.value,
    currentChapter: currentChapter.value,
    position: 'after'
  }).map(r => r.result).filter(Boolean)
})

const pluginWorkspaceTabs = computed(() => {
  return pluginManager.callHook('workspace.tabs', {
    workspace: workspace.value,
    chapters: chapters.value
  }).map(r => r.result).filter(Boolean).sort((a, b) => (a.order || 100) - (b.order || 100))
})

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
    
    // 从 workspace.config 加载模型配置
    if (workspace.value && workspace.value.config) {
      const config = workspace.value.config
      if (config.model !== undefined) systemConfig.value.model = config.model
      if (config.temperature !== undefined) systemConfig.value.temperature = config.temperature
      if (config.max_tokens !== undefined) systemConfig.value.max_tokens = config.max_tokens
      if (config.top_p !== undefined) systemConfig.value.top_p = config.top_p
      if (config.top_k !== undefined) systemConfig.value.top_k = config.top_k
      if (config.frequency_penalty !== undefined) systemConfig.value.frequency_penalty = config.frequency_penalty
      if (config.presence_penalty !== undefined) systemConfig.value.presence_penalty = config.presence_penalty
      if (config.logit_bias !== undefined) {
        systemConfig.value.logit_bias = config.logit_bias
        logitBiasText.value = JSON.stringify(config.logit_bias, null, 2)
      }
    }
    
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
    
    // 获取后端插件
    const backendPlugins = await pluginAPI.list()
    
    // 获取前端插件（包括禁用的）
    const frontendPlugins = pluginManager.getPlugins().map(plugin => ({
      name: plugin.name,
      version: plugin.version || '1.0.0',
      description: plugin.description || '前端插件',
      author: plugin.author || '',
      is_frontend: true,
      is_frontend_enabled: plugin.enabled,
      config_schema: null
    }))
    
    // 合并插件列表：前端插件在前，后端插件在后
    availablePlugins.value = [...frontendPlugins, ...backendPlugins]
    
    // 获取当前工作空间的插件配置
    const configData = await pluginAPI.getConfig(workspaceId.value)
    pluginsConfig.value = configData.plugins || {}
    
    // 设置默认激活的插件Tab
    if (availablePlugins.value.length > 0 && !activePluginTab.value) {
      activePluginTab.value = availablePlugins.value[0].name
    }
  } catch (error) {
    console.error('加载插件失败:', error)
    message.error('加载插件失败: ' + error.message)
  } finally {
    pluginsLoading.value = false
  }
}

function isPluginEnabled(pluginName) {
  // 前端插件根据配置文件决定
  const plugin = availablePlugins.value.find(p => p.name === pluginName)
  if (plugin?.is_frontend) {
    return plugin.is_frontend_enabled
  }
  return pluginsConfig.value[pluginName]?.enabled !== false
}

function getPluginConfig(pluginName) {
  return pluginsConfig.value[pluginName] || {}
}

async function togglePlugin(pluginName, enabled) {
  // 前端插件不允许禁用
  const plugin = availablePlugins.value.find(p => p.name === pluginName)
  if (plugin?.is_frontend) {
    message.warning('前端插件不能禁用')
    return
  }
  
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
        ...(pluginsConfig.value[pluginName] || {}),
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
  planChatActive.value = true
  planChatMessages.value = []
  planCompleted.value = false
  currentPlanChapterId.value = null
  newChapterNumber.value = chapters.value.length + 1
}

// 发送消息
async function sendMessage() {
  if (!userMessage.value.trim() || planGenerating.value) return
  
  planChatMessages.value.push({
    role: 'user',
    content: userMessage.value
  })
  
  userMessage.value = ''
  
  // 自动滚动
  setTimeout(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }, 50)
  
  await continueChat()
}

// 继续对话
async function continueChat() {
  try {
    planGenerating.value = true
    
    // 获取生成参数
    const genParams = {}
    if (systemConfig.value.temperature !== null && systemConfig.value.temperature !== undefined) {
      genParams.temperature = systemConfig.value.temperature
    }
    if (systemConfig.value.max_tokens !== null && systemConfig.value.max_tokens !== undefined) {
      genParams.max_tokens = systemConfig.value.max_tokens
    }
    if (systemConfig.value.top_p !== null && systemConfig.value.top_p !== undefined) {
      genParams.top_p = systemConfig.value.top_p
    }
    if (systemConfig.value.top_k !== null && systemConfig.value.top_k !== undefined) {
      genParams.top_k = systemConfig.value.top_k
    }
    if (systemConfig.value.frequency_penalty !== null && systemConfig.value.frequency_penalty !== undefined) {
      genParams.frequency_penalty = systemConfig.value.frequency_penalty
    }
    if (systemConfig.value.presence_penalty !== null && systemConfig.value.presence_penalty !== undefined) {
      genParams.presence_penalty = systemConfig.value.presence_penalty
    }
    if (systemConfig.value.logit_bias !== null && systemConfig.value.logit_bias !== undefined) {
      genParams.logit_bias = systemConfig.value.logit_bias
    }
    
    const result = await generationAPI.planInteractive({
      workspace_id: workspaceId.value,
      chapter_number: newChapterNumber.value,
      messages: planChatMessages.value,
      ...genParams
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
  planChatActive.value = false
  planChatMessages.value = []
  userMessage.value = ''
  planGenerating.value = false
  planCompleted.value = false
  currentPlanChapterId.value = null
  editingMessageIndex.value = null
  editingMessageContent.value = ''
  newChapterNumber.value = chapters.value.length + 1
}

// 开始编辑消息
function startEditMessage(index, content) {
  editingMessageIndex.value = index
  editingMessageContent.value = content
}

// 取消编辑消息
function cancelEditMessage() {
  editingMessageIndex.value = null
  editingMessageContent.value = ''
}

// 保存编辑并重新生成
async function saveEditMessage(index) {
  if (!editingMessageContent.value.trim()) {
    message.warning('消息内容不能为空')
    return
  }
  
  // 更新消息内容
  planChatMessages.value[index].content = editingMessageContent.value
  
  // 删除该消息之后的所有消息
  planChatMessages.value = planChatMessages.value.slice(0, index + 1)
  
  // 重置编辑状态
  editingMessageIndex.value = null
  editingMessageContent.value = ''
  
  // 重新生成
  await continueChat()
}

// 删除消息及之后的所有消息
function deleteMessageFrom(index) {
  dialog.warning({
    title: '确认删除',
    content: '删除此消息后，之后的所有对话也会被删除。确定吗？',
    positiveText: '确认',
    negativeText: '取消',
    onPositiveClick: () => {
      planChatMessages.value = planChatMessages.value.slice(0, index)
      message.success('已删除')
    }
  })
}

// 重新生成（从某条用户消息开始）
async function regenerateFromMessage(index) {
  // 删除该消息之后的所有消息
  planChatMessages.value = planChatMessages.value.slice(0, index + 1)
  
  // 重新生成
  await continueChat()
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
  const baseActions = [
    { label: '回退到此章节', key: 'rollback' },
    { label: '删除', key: 'delete' }
  ]
  
  // 添加插件注册的章节操作
  const pluginActions = pluginManager.callHook('sidebar.chapter.actions', {
    chapter,
    workspace: workspace.value
  }).map(r => r.result).filter(Boolean)
  
  return [...baseActions, ...pluginActions]
}

async function handleChapterAction(key, chapter) {
  // 处理内置操作
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
    return
  }
  
  // 处理插件操作
  const pluginActions = pluginManager.callHook('sidebar.chapter.actions', {
    chapter,
    workspace: workspace.value
  }).map(r => r.result).filter(Boolean)
  
  const pluginAction = pluginActions.find(a => a.key === key)
  if (pluginAction && pluginAction.handler) {
    try {
      await pluginAction.handler(chapter)
    } catch (error) {
      message.error('操作失败: ' + error.message)
    }
  }
}

// 解析logit_bias JSON
function parseLogitBias() {
  if (!logitBiasText.value.trim()) {
    systemConfig.value.logit_bias = null
    return
  }
  
  try {
    const parsed = JSON.parse(logitBiasText.value)
    systemConfig.value.logit_bias = parsed
  } catch (e) {
    message.error('Logit Bias JSON格式错误')
    systemConfig.value.logit_bias = null
  }
}

// 系统设置相关函数
function resetSystemConfig() {
  systemConfig.value = {
    model: null,
    temperature: 0.7,
    max_tokens: 2000,
    top_p: null,
    top_k: null,
    frequency_penalty: null,
    presence_penalty: null,
    logit_bias: null
  }
  logitBiasText.value = ''
  message.info('已重置为默认值')
}

async function saveSystemConfig() {
  try {
    savingSystemConfig.value = true
    
    // 保存前先解析一次logit_bias
    parseLogitBias()
    
    // 准备要保存的配置，只保存非null的值
    const configToSave = { ...workspace.value.config }
    
    // 模型配置参数
    if (systemConfig.value.model !== null && systemConfig.value.model !== '') configToSave.model = systemConfig.value.model
    if (systemConfig.value.temperature !== null) configToSave.temperature = systemConfig.value.temperature
    if (systemConfig.value.max_tokens !== null) configToSave.max_tokens = systemConfig.value.max_tokens
    if (systemConfig.value.top_p !== null) configToSave.top_p = systemConfig.value.top_p
    if (systemConfig.value.top_k !== null) configToSave.top_k = systemConfig.value.top_k
    if (systemConfig.value.frequency_penalty !== null) configToSave.frequency_penalty = systemConfig.value.frequency_penalty
    if (systemConfig.value.presence_penalty !== null) configToSave.presence_penalty = systemConfig.value.presence_penalty
    if (systemConfig.value.logit_bias !== null) configToSave.logit_bias = systemConfig.value.logit_bias
    
    // 调用API保存到 workspace.config
    await workspaceAPI.update(workspaceId.value, { config: configToSave })
    
    // 重新加载 workspace 以更新本地状态
    await workspaceStore.loadWorkspace(workspaceId.value)
    
    message.success('模型配置已保存')
  } catch (error) {
    message.error('保存失败: ' + error.message)
  } finally {
    savingSystemConfig.value = false
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

/* 左侧垂直工具栏 */
.workspace-toolbar {
  background: rgba(255, 255, 255, 0.02);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.toolbar-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 0;
}

.toolbar-item {
  width: 60px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.5);
  transition: all 0.2s;
  position: relative;
}

.toolbar-item:hover {
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.06);
}

.toolbar-item.active {
  color: rgba(102, 126, 234, 0.95);
  background: rgba(102, 126, 234, 0.12);
}

.toolbar-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 3px;
  background: rgba(102, 126, 234, 0.95);
  border-radius: 0 2px 2px 0;
}

.toolbar-item svg {
  width: 24px;
  height: 24px;
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
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 35px;
  padding: 0 12px 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.sidebar-title {
  font-size: 11px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.new-chapter-icon-btn {
  color: rgba(255, 255, 255, 0.5);
  padding: 4px;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.new-chapter-icon-btn:hover {
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.08);
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

/* Chapter Tree - VSCode风格 */
.chapter-tree {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 4px 0;
}

/* 章节列表动画 */
.chapter-list-enter-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.chapter-list-leave-active {
  transition: all 0.3s ease-out;
  position: absolute;
  width: 100%;
}

.chapter-list-enter-from {
  opacity: 0;
  transform: translateX(-20px) scale(0.9);
}

.chapter-list-leave-to {
  opacity: 0;
  transform: translateX(20px) scale(0.9);
}

.chapter-list-move {
  transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.chapter-tree-item {
  position: relative;
  user-select: none;
  cursor: pointer;
}

.chapter-tree-item-content {
  display: flex;
  align-items: center;
  height: 22px;
  padding: 0 12px 0 20px;
  gap: 7px;
  transition: background 0.05s;
}

.chapter-tree-item:hover .chapter-tree-item-content {
  background: rgba(255, 255, 255, 0.08);
}

.chapter-tree-item.active .chapter-tree-item-content {
  background: rgba(255, 255, 255, 0.12);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

.status-dot.status-completed {
  background: rgba(99, 226, 183, 0.9);
}

.status-dot.status-generating,
.status-dot.status-verifying,
.status-dot.status-improving {
  background: rgba(240, 186, 82, 0.9);
}

.status-dot.status-failed {
  background: rgba(242, 99, 123, 0.9);
}

.chapter-label {
  flex: 1;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 22px;
}

.chapter-subtitle {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

.chapter-actions {
  opacity: 0;
  transition: opacity 0.1s;
}

.chapter-tree-item:hover .chapter-actions {
  opacity: 1;
}

.chapter-more {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  color: rgba(255, 255, 255, 0.6);
  transition: all 0.1s;
  border-radius: 2px;
}

.chapter-more:hover {
  color: rgba(255, 255, 255, 0.95);
  background: rgba(255, 255, 255, 0.12);
}

.chapter-more svg {
  display: block;
}

/* 主内容区 */
.main-content {
  height: 100%;
  overflow: hidden;
  background: #101014;
  display: flex;
  flex-direction: column;
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
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px 20px;
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

/* Plan Chat View - VSCode交互式窗口风格 */
.plan-chat-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #101014;
}

.plan-chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 42px;
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 500;
}

.header-title svg {
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.6);
}

.close-btn {
  color: rgba(255, 255, 255, 0.5);
  padding: 4px;
}

.close-btn:hover {
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.08);
}

.plan-chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-message {
  display: flex;
  gap: 10px;
  animation: fadeIn 0.2s ease-out;
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

.chat-message.user .message-avatar {
  background: rgba(102, 126, 234, 0.2);
  color: rgba(102, 126, 234, 0.95);
}

.chat-message.assistant .message-avatar {
  background: rgba(99, 226, 183, 0.15);
  color: rgba(99, 226, 183, 0.9);
}

.message-bubble {
  flex: 1;
  min-width: 0;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.04);
  border-left: 2px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

.chat-message.user .message-bubble {
  border-left-color: rgba(102, 126, 234, 0.4);
}

.chat-message.assistant .message-bubble {
  border-left-color: rgba(99, 226, 183, 0.4);
}

.message-content-wrapper {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.message-text {
  font-size: 13px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.85);
  white-space: pre-wrap;
  word-break: break-word;
  flex: 1;
}

.message-actions {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s;
  flex-shrink: 0;
}

.chat-message:hover .message-actions {
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

.message-edit {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.edit-input :deep(.n-input-wrapper) {
  padding: 0;
}

.edit-input :deep(.n-input__border),
.edit-input :deep(.n-input__state-border) {
  border: none;
}

.edit-input :deep(.n-input__textarea-el) {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(102, 126, 234, 0.3);
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  line-height: 1.6;
  padding: 8px 12px;
  border-radius: 2px;
}

.edit-input :deep(.n-input__textarea-el):focus {
  border-color: rgba(102, 126, 234, 0.6);
  background: rgba(255, 255, 255, 0.08);
  outline: none;
}

.edit-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.plan-completed-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: rgba(99, 226, 183, 0.1);
  border-top: 1px solid rgba(99, 226, 183, 0.2);
  border-bottom: 1px solid rgba(99, 226, 183, 0.2);
  color: rgba(99, 226, 183, 0.95);
  font-size: 13px;
  font-weight: 500;
}

.plan-completed-banner svg {
  flex-shrink: 0;
}

.plan-completed-banner span {
  flex: 1;
}

.plan-chat-input {
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
}

.chat-input :deep(.n-input__textarea-el):focus {
  border-color: rgba(102, 126, 234, 0.5);
  background: rgba(255, 255, 255, 0.06);
  outline: none;
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

/* 工作区内容样式 */
.workspace-content {
  height: 100%;
  overflow-y: auto;
  background: #101014;
}

.workspace-container {
  height: 100%;
  display: flex;
  flex-direction: row;
}

/* VSCode风格的垂直二级Tab */
.workspace-tabs-vertical {
  height: 100%;
  display: flex;
  flex-direction: row;
}

.workspace-tabs-vertical :deep(.n-tabs-nav) {
  width: 180px;
  padding: 8px 0;
  background: rgba(255, 255, 255, 0.02);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.workspace-tabs-vertical :deep(.n-tabs-nav-scroll-content) {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.workspace-tabs-vertical :deep(.n-tabs-tab) {
  padding: 0 20px;
  height: 32px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  border: none;
  background: transparent;
  transition: all 0.15s;
  justify-content: flex-start;
  border-left: 2px solid transparent;
}

.workspace-tabs-vertical :deep(.n-tabs-tab:hover) {
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.05);
}

.workspace-tabs-vertical :deep(.n-tabs-tab.n-tabs-tab--active) {
  color: rgba(255, 255, 255, 0.95);
  background: rgba(255, 255, 255, 0.08);
  border-left-color: rgba(102, 126, 234, 0.9);
}

.workspace-tabs-vertical :deep(.n-tabs-bar) {
  display: none;
}

.workspace-tabs-vertical :deep(.n-tabs-pane-wrapper) {
  flex: 1;
  overflow: hidden;
}

.tab-content {
  height: 100%;
  overflow-y: auto;
  padding: 32px 40px;
}

.workspace-inner {
  padding: 32px 40px;
}

.workspace-header {
  margin-bottom: 32px;
}

.workspace-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 8px 0;
}

.workspace-header p {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

/* 插件详情页 */
.plugin-detail {
  animation: fadeIn 0.3s ease-out;
}

.plugin-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  margin-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.plugin-detail-info {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.plugin-detail-name {
  font-size: 24px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.plugin-badge-builtin {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  background: rgba(24, 160, 88, 0.15);
  border: 1px solid rgba(24, 160, 88, 0.3);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  color: #18a058;
  letter-spacing: 0.5px;
}

.plugin-status-builtin-enabled {
  font-size: 14px;
  font-weight: 500;
  color: rgba(24, 160, 88, 0.9);
  padding: 8px 16px;
  background: rgba(24, 160, 88, 0.1);
  border-radius: 18px;
  border: 1px solid rgba(24, 160, 88, 0.2);
}

.plugin-status-builtin-disabled {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.4);
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.plugin-detail-version {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
}

.plugin-detail-description {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  margin-bottom: 32px;
}

.plugin-detail-config {
  margin-top: 32px;
}

.config-section-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 16px 0;
}

/* 系统设置工作区 - VSCode风格 */
.settings-section {
  animation: fadeIn 0.3s ease-out;
}

.settings-section-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.settings-actions {
  display: flex;
  gap: 12px;
}

.settings-content {
  padding: 0;
}

.setting-item {
  padding: 20px 0;
}

.setting-item:hover {
  background: transparent;
}

.setting-header {
  margin-bottom: 12px;
}

.setting-title {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 6px;
  letter-spacing: -0.01em;
}

.setting-description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.6;
  max-width: 700px;
}

.setting-control {
  margin-top: 12px;
}

.control-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.setting-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 8px;
  font-style: italic;
}

.setting-divider {
  margin: 0 !important;
  background: rgba(255, 255, 255, 0.06);
}

/* 工作区切换动画 */
.workspace-fade-enter-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.workspace-fade-leave-active {
  transition: opacity 0.15s ease;
}

.workspace-fade-enter-from {
  opacity: 0;
  transform: translateX(12px);
}

.workspace-fade-leave-to {
  opacity: 0;
}
</style>

