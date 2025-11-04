import { createRouter, createWebHistory } from 'vue-router'
import { authAPI } from '../services/api'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    name: 'WorkspaceList',
    component: () => import('../views/WorkspaceList.vue'),
    meta: { title: '我的小说', requiresAuth: true }
  },
  {
    path: '/workspace/:id',
    name: 'Editor',
    component: () => import('../views/Editor.vue'),
    meta: { title: '编辑器', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查是否需要登录
router.beforeEach(async (to, from, next) => {
  // 不需要认证的页面直接放行
  if (to.meta.requiresAuth === false) {
    next()
    return
  }
  
  try {
    // 检查系统是否需要密码
    const { requires_password } = await authAPI.check()
    
    if (!requires_password) {
      // 系统没有设置密码，直接放行
      next()
      return
    }
    
    // 需要密码，检查是否已登录
    const token = localStorage.getItem('access_token')
    if (!token) {
      // 未登录，跳转到登录页
      next('/login')
      return
    }
    
    // 已登录，放行
    next()
  } catch (error) {
    console.error('路由守卫错误:', error)
    // 出错了也放行，让拦截器处理
    next()
  }
})

// 动态更新页面标题
router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - Novel Studio` : 'Novel Studio'
})

export default router

