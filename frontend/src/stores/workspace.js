import { defineStore } from 'pinia'
import { ref } from 'vue'
import { workspaceAPI, chapterAPI } from '../services/api'

export const useWorkspaceStore = defineStore('workspace', () => {
  const workspaces = ref([])
  const currentWorkspace = ref(null)
  const chapters = ref([])
  const loading = ref(false)

  // 加载工作区列表
  async function loadWorkspaces() {
    loading.value = true
    try {
      workspaces.value = await workspaceAPI.list()
    } catch (error) {
      console.error('加载工作区失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 加载工作区详情
  async function loadWorkspace(id) {
    loading.value = true
    try {
      currentWorkspace.value = await workspaceAPI.get(id)
      await loadChapters(id)
    } catch (error) {
      console.error('加载工作区失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建工作区
  async function createWorkspace(data) {
    loading.value = true
    try {
      const workspace = await workspaceAPI.create(data)
      workspaces.value.unshift(workspace)
      return workspace
    } catch (error) {
      console.error('创建工作区失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新工作区
  async function updateWorkspace(id, data) {
    loading.value = true
    try {
      const workspace = await workspaceAPI.update(id, data)
      const index = workspaces.value.findIndex(ws => ws.id === id)
      if (index !== -1) {
        workspaces.value[index] = workspace
      }
      if (currentWorkspace.value?.id === id) {
        currentWorkspace.value = workspace
      }
      return workspace
    } catch (error) {
      console.error('更新工作区失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除工作区
  async function deleteWorkspace(id) {
    loading.value = true
    try {
      await workspaceAPI.delete(id)
      workspaces.value = workspaces.value.filter(ws => ws.id !== id)
    } catch (error) {
      console.error('删除工作区失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 加载章节列表
  async function loadChapters(workspaceId) {
    try {
      chapters.value = await chapterAPI.list(workspaceId)
    } catch (error) {
      console.error('加载章节失败:', error)
      throw error
    }
  }

  // 回退到指定章节
  async function rollbackToChapter(workspaceId, chapterId) {
    loading.value = true
    try {
      await chapterAPI.rollback(workspaceId, chapterId)
      await loadChapters(workspaceId)
    } catch (error) {
      console.error('回退失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    workspaces,
    currentWorkspace,
    chapters,
    loading,
    loadWorkspaces,
    loadWorkspace,
    createWorkspace,
    updateWorkspace,
    deleteWorkspace,
    loadChapters,
    rollbackToChapter
  }
})

