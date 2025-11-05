import { defineStore } from 'pinia'
import { ref } from 'vue'
import { generationAPI, chapterAPI } from '../services/api'

export const useGenerationStore = defineStore('generation', () => {
  const currentChapter = ref(null)
  const loading = ref(false)
  const stage = ref('idle') // idle, planning, generating, verifying, improving

  // 生成内容
  async function generateContent(chapterId, regenerate = false, model = null) {
    loading.value = true
    stage.value = 'generating'
    try {
      const result = await generationAPI.generate({
        chapter_id: chapterId,
        regenerate,
        model
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
  async function verifyContent(chapterId, model = null) {
    loading.value = true
    stage.value = 'verifying'
    try {
      const result = await generationAPI.verify({
        chapter_id: chapterId,
        model
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
  async function improveContent(chapterId, focusIssues = null, model = null) {
    loading.value = true
    stage.value = 'improving'
    try {
      const result = await generationAPI.improve({
        chapter_id: chapterId,
        focus_issues: focusIssues,
        model
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
    generateContent,
    verifyContent,
    improveContent,
    finalizeChapter,
    loadChapter
  }
})

