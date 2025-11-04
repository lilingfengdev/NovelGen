import { defineStore } from 'pinia'
import { ref } from 'vue'
import { generationAPI, chapterAPI } from '../services/api'

export const useGenerationStore = defineStore('generation', () => {
  const currentChapter = ref(null)
  const loading = ref(false)
  const stage = ref('idle') // idle, planning, generating, verifying, improving

  // 获取系统配置的生成参数
  function getGenerationParams() {
    try {
      const config = localStorage.getItem('systemConfig')
      if (config) {
        const parsed = JSON.parse(config)
        // 只返回非null的参数，保证兼容性
        const params = {}
        if (parsed.temperature !== null && parsed.temperature !== undefined) {
          params.temperature = parsed.temperature
        }
        if (parsed.max_tokens !== null && parsed.max_tokens !== undefined) {
          params.max_tokens = parsed.max_tokens
        }
        if (parsed.top_p !== null && parsed.top_p !== undefined) {
          params.top_p = parsed.top_p
        }
        if (parsed.top_k !== null && parsed.top_k !== undefined) {
          params.top_k = parsed.top_k
        }
        if (parsed.frequency_penalty !== null && parsed.frequency_penalty !== undefined) {
          params.frequency_penalty = parsed.frequency_penalty
        }
        if (parsed.presence_penalty !== null && parsed.presence_penalty !== undefined) {
          params.presence_penalty = parsed.presence_penalty
        }
        if (parsed.logit_bias !== null && parsed.logit_bias !== undefined) {
          params.logit_bias = parsed.logit_bias
        }
        return params
      }
    } catch (e) {
      console.error('读取配置失败:', e)
    }
    return {}
  }

  // 生成大纲
  async function createPlan(workspaceId, chapterNumber, userInput = null) {
    loading.value = true
    stage.value = 'planning'
    try {
      const result = await generationAPI.plan({
        workspace_id: workspaceId,
        chapter_number: chapterNumber,
        user_input: userInput
      })
      currentChapter.value = await chapterAPI.get(result.chapter_id)
      return result
    } catch (error) {
      console.error('生成大纲失败:', error)
      throw error
    } finally {
      loading.value = false
      stage.value = 'idle'
    }
  }

  // 生成内容
  async function generateContent(chapterId, regenerate = false) {
    loading.value = true
    stage.value = 'generating'
    try {
      const result = await generationAPI.generate({
        chapter_id: chapterId,
        regenerate,
        ...getGenerationParams()
      })
      currentChapter.value = await chapterAPI.get(chapterId)
      return result
    } catch (error) {
      console.error('生成内容失败:', error)
      throw error
    } finally {
      loading.value = false
      stage.value = 'idle'
    }
  }

  // 验证内容
  async function verifyContent(chapterId) {
    loading.value = true
    stage.value = 'verifying'
    try {
      const result = await generationAPI.verify({
        chapter_id: chapterId,
        ...getGenerationParams()
      })
      currentChapter.value = await chapterAPI.get(chapterId)
      return result
    } catch (error) {
      console.error('验证失败:', error)
      throw error
    } finally {
      loading.value = false
      stage.value = 'idle'
    }
  }

  // 改进内容
  async function improveContent(chapterId, focusIssues = null) {
    loading.value = true
    stage.value = 'improving'
    try {
      const result = await generationAPI.improve({
        chapter_id: chapterId,
        focus_issues: focusIssues,
        ...getGenerationParams()
      })
      currentChapter.value = await chapterAPI.get(chapterId)
      return result
    } catch (error) {
      console.error('改进失败:', error)
      throw error
    } finally {
      loading.value = false
      stage.value = 'idle'
    }
  }

  // 最终确认
  async function finalizeChapter(chapterId) {
    loading.value = true
    try {
      const result = await generationAPI.finalize(chapterId)
      currentChapter.value = await chapterAPI.get(chapterId)
      return result
    } catch (error) {
      console.error('确认失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 加载章节
  async function loadChapter(chapterId) {
    loading.value = true
    try {
      currentChapter.value = await chapterAPI.get(chapterId)
    } catch (error) {
      console.error('加载章节失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    currentChapter,
    loading,
    stage,
    createPlan,
    generateContent,
    verifyContent,
    improveContent,
    finalizeChapter,
    loadChapter
  }
})

