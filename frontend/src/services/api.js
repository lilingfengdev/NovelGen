import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

// Workspace API
export const workspaceAPI = {
  list: (params) => api.get('/workspace', { params }),
  get: (id) => api.get(`/workspace/${id}`),
  create: (data) => api.post('/workspace', data),
  update: (id, data) => api.put(`/workspace/${id}`, data),
  delete: (id) => api.delete(`/workspace/${id}`)
}

// Chapter API
export const chapterAPI = {
  list: (workspaceId, params) => api.get(`/workspace/${workspaceId}/chapters`, { params }),
  get: (id) => api.get(`/chapters/${id}`),
  delete: (id) => api.delete(`/chapters/${id}`),
  rollback: (workspaceId, chapterId) => api.post(`/workspace/${workspaceId}/rollback/${chapterId}`)
}

// Generation API
export const generationAPI = {
  plan: (data) => api.post('/plan', data),
  planInteractive: (data) => api.post('/plan/interactive', data),
  generate: (data) => api.post('/generate', data),
  verify: (data) => api.post('/verify', data),
  improve: (data) => api.post('/improve', data),
  finalize: (chapterId) => api.post(`/finalize/${chapterId}`)
}

// Plugin API
export const pluginAPI = {
  list: () => api.get('/plugins'),
  getConfig: (workspaceId) => api.get(`/plugins/${workspaceId}/config`),
  updateConfig: (workspaceId, data) => api.put(`/plugins/${workspaceId}/config`, data),
  toggle: (workspaceId, pluginName, enabled) => api.put(`/plugins/${workspaceId}/${pluginName}/toggle`, { enabled })
}

export default api

