<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="logo">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
          <h1>Novel Studio</h1>
          <p class="subtitle">输入密码以继续</p>
        </div>
        
        <n-form ref="formRef" :model="formData" :rules="rules" @submit.prevent="handleLogin">
          <n-form-item path="password">
            <n-input
              v-model:value="formData.password"
              type="password"
              show-password-on="click"
              placeholder="请输入访问密码"
              size="large"
              @keyup.enter="handleLogin"
              :disabled="loading"
            >
              <template #prefix>
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
              </template>
            </n-input>
          </n-form-item>
          
          <n-button
            type="primary"
            size="large"
            block
            :loading="loading"
            @click="handleLogin"
            class="login-btn"
          >
            登录
          </n-button>
        </n-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { NForm, NFormItem, NInput, NButton } from 'naive-ui'
import { authAPI } from '../services/api'

const router = useRouter()
const message = useMessage()

const formData = ref({
  password: ''
})

const formRef = ref(null)
const loading = ref(false)

const rules = {
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

onMounted(async () => {
  // 检查是否已经登录
  const token = localStorage.getItem('access_token')
  if (token) {
    router.replace('/')
  }
})

async function handleLogin() {
  // 验证表单
  formRef.value?.validate(async (errors) => {
    if (errors) {
      return
    }
    
    loading.value = true
    try {
      const response = await authAPI.login(formData.value.password)
      // 保存 token
      localStorage.setItem('access_token', response.access_token)
      message.success('登录成功')
      // 跳转到首页
      router.replace('/')
    } catch (error) {
      message.error(error.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-page {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a24 0%, #0f0f14 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.login-page::before {
  content: '';
  position: absolute;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  top: -200px;
  right: -200px;
  animation: float 20s infinite;
}

.login-page::after {
  content: '';
  position: absolute;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(168, 85, 247, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  bottom: -150px;
  left: -150px;
  animation: float 15s infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, 30px); }
}

.login-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.login-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 48px 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 16px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.login-btn {
  margin-top: 8px;
  font-weight: 500;
  height: 44px;
}

/* 响应式 */
@media (max-width: 768px) {
  .login-card {
    padding: 40px 24px;
  }
  
  .login-header h1 {
    font-size: 24px;
  }
}
</style>

