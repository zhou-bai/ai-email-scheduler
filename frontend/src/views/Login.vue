<template>
  <div class="auth-container">
    <div class="auth-wrapper">
      <div class="auth-brand">
        <img class="brand-logo" src="../assets/logo.svg" alt="AI Email Scheduler" />
        <h1>AI Email Scheduler</h1>
        <p>Intelligent email scheduling to manage every message</p>
      </div>

      <el-card class="auth-card" shadow="hover">
        <div class="auth-header">
          <h2>Welcome back</h2>
          <p>Sign in to manage email summaries and schedules</p>
        </div>
        <el-form
          ref="loginForm"
          :model="form"
          :rules="rules"
          label-position="top"
          @submit.prevent
        >
          <el-form-item label="Email" prop="email">
            <el-input
              v-model="form.email"
              placeholder="Enter your email"
              autocomplete="email"
            />
          </el-form-item>
          <el-form-item label="Password" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="Enter your password"
              autocomplete="current-password"
              show-password
            />
          </el-form-item>
          <div class="auth-options">
            <el-checkbox v-model="form.remember">Remember me</el-checkbox>
            <el-link type="primary" :underline="false">Forgot password?</el-link>
          </div>
          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              class="auth-submit"
              @click="handleSubmit"
            >
              Sign In
            </el-button>
          </el-form-item>
        </el-form>
        <el-divider content-position="center">or</el-divider>
        <p class="auth-footer">
          Don’t have an account?
          <router-link to="/register">Sign up</router-link>
        </p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { setToken, login } from '../api'

const loginForm = ref(null)
const loading = ref(false)
const router = useRouter()
const route = useRoute()

const form = reactive({
  email: '',
  password: '',
  remember: true
})

const rules = {
  email: [
    { required: true, message: 'Please enter email', trigger: 'blur' },
    {
      type: 'email',
      message: 'Please enter a valid email',
      trigger: ['blur', 'change']
    }
  ],
  password: [
    { required: true, message: 'Please enter password', trigger: 'blur' },
    {
      min: 6,
      message: 'Password must be at least 6 characters',
      trigger: ['blur', 'change']
    }
  ]
}

const handleSubmit = () => {
  loginForm.value?.validate(async (valid) => {
    if (!valid) return
    loading.value = true

    try {
      // 真实的登录请求
      await login({
        email: form.email,
        password: form.password
      }).then(() => {
        ElMessage.success('Signed in')
        setToken('demo-token')
        const redirect = '/'
        router.push(redirect)
      })
    } catch (error) {
      ElMessage.error('Sign in failed, please try again later')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 48px 24px;
  background: radial-gradient(circle at top left, #eaf4ff, transparent 55%),
    radial-gradient(circle at bottom right, #eefbf1, transparent 45%),
    linear-gradient(135deg, #f6f8fb, #ffffff);
}

.auth-wrapper {
  width: 100%;
  max-width: 960px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 48px;
  align-items: center;
}

.auth-brand {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 16px;
  color: #1f2d3d;
}

.auth-brand h1 {
  font-size: 32px;
  margin: 0;
  letter-spacing: 0.04em;
}

.auth-brand p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  border: none;
  border-radius: 24px;
  padding: 32px 36px;
  box-shadow: 0 24px 48px rgba(31, 45, 61, 0.08);
}

.auth-header {
  margin-bottom: 32px;
}

.auth-header h2 {
  margin: 0 0 8px;
  font-size: 28px;
  color: #1f2d3d;
}

.auth-header p {
  margin: 0;
  color: #909399;
}

.auth-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.auth-title {
  text-align: center;
  margin-bottom: 16px;
}

.auth-submit {
  width: 100%;
}

.social-login {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.auth-footer {
  margin-top: 16px;
  text-align: center;
  color: #606266;
}

.auth-footer a {
  color: var(--el-color-primary);
}

@media (max-width: 768px) {
  .auth-wrapper {
    gap: 32px;
  }

  .auth-card {
    max-width: 100%;
    padding: 28px 24px;
  }

  .auth-header h2 {
    font-size: 24px;
  }
}

.brand-logo {
  width: 300px;
  height: 300px;
}
</style>

