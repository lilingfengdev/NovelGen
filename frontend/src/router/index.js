import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'WorkspaceList',
    component: () => import('../views/WorkspaceList.vue'),
    meta: { title: '我的小说' }
  },
  {
    path: '/workspace/:id',
    name: 'Editor',
    component: () => import('../views/Editor.vue'),
    meta: { title: '编辑器' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 动态更新页面标题
router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - Novel Studio` : 'Novel Studio'
})

export default router

