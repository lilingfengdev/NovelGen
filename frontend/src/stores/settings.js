import { defineStore } from 'pinia'
import { settingsAPI } from '../services/api'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    settings: {
      openai_api_key: '',
      openai_base_url: '',
      openai_model: 'gpt-4-turbo-preview',
      access_password: ''
    },
    publicInfo: {
      has_password: false,
      has_api_key: false
    },
    loading: false
  }),

  actions: {
    async loadSettings() {
      this.loading = true
      try {
        const data = await settingsAPI.get()
        this.settings = data
      } catch (error) {
        console.error('加载设置失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async loadPublicInfo() {
      try {
        const data = await settingsAPI.getPublic()
        this.publicInfo = data
      } catch (error) {
        console.error('加载公开信息失败:', error)
      }
    },

    async updateSettings(data) {
      this.loading = true
      try {
        const result = await settingsAPI.update(data)
        this.settings = result
        return result
      } catch (error) {
        console.error('更新设置失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async resetSettings() {
      this.loading = true
      try {
        await settingsAPI.reset()
        await this.loadSettings()
      } catch (error) {
        console.error('重置设置失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})

