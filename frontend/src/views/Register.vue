<template>
  <div class="auth-container">
    <div class="auth-wrapper">
      <div class="auth-brand">
        <img class="brand-logo" src="../assets/logo.svg" alt="AI Email Scheduler" />
        <h1>AI Email Scheduler</h1>
        <p>Join our intelligent email platform and stay on top of every schedule</p>
        <ul class="benefits">
          <li>Automatically summarize daily email highlights</li>
          <li>Intelligently create meetings and tasks</li>
        </ul>
      </div>

      <el-card class="auth-card" shadow="hover">
        <div class="auth-header">
          <h2>Create Account</h2>
          <p>Fill the form to start your intelligent email experience</p>
        </div>
        <el-form
          ref="registerForm"
          :model="form"
          :rules="rules"
          label-position="top"
          @submit.prevent
        >
          <el-form-item label="Name" prop="name">
            <el-input
              v-model="form.name"
              placeholder="Enter your name"
              autocomplete="name"
            />
          </el-form-item>
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
              autocomplete="new-password"
              show-password
            />
          </el-form-item>
          <el-form-item label="Confirm Password" prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="Re-enter your password"
              autocomplete="new-password"
              show-password
            />
          </el-form-item>
          <el-alert
            class="password-tips"
            title="Password must be at least 6 characters, and include mixed cases or special symbols for better security"
            type="info"
            :closable="false"
          />
          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              class="auth-submit"
              @click="handleSubmit"
            >
              Sign Up
            </el-button>
          </el-form-item>
        </el-form>
        <p class="auth-footer">
          Already have an account?
          <router-link to="/login">Sign in</router-link>
        </p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { setToken, register } from '../api'

const registerForm = ref(null)
const loading = ref(false)
const router = useRouter()

const form = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('Please confirm your password'))
    return
  }
  if (value !== form.password) {
    callback(new Error('Passwords do not match'))
    return
  }
  callback()
}

const rules = {
  name: [
    { required: true, message: 'Please enter name', trigger: 'blur' },
    {
      min: 2,
      message: 'Name must be at least 2 characters',
      trigger: ['blur', 'change']
    }
  ],
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
  ],
  confirmPassword: [
    {
      validator: validateConfirmPassword,
      trigger: ['blur', 'change']
    }
  ]
}

const handleSubmit = () => {
  registerForm.value?.validate(async (valid) => {
    if (!valid) return
    loading.value = true

    try {
      // 真实的注册请求
      // await register({
      //   name: form.name,
      //   email: form.email,
      //   password: form.password
      // }).then(() => {
      //   ElMessage.success('Signed up')
      //   router.push('/')
      // })
      // 模拟注册
      await new Promise((resolve) => setTimeout(resolve, 1000))
      setToken('demo-token')
      ElMessage.success('Signed up (demo)')
      router.push('/')
    } catch (error) {
      ElMessage.error('Sign up failed, please try again later')
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
  background: radial-gradient(circle at top right, #f3faff, transparent 55%),
    radial-gradient(circle at bottom left, #fef4ec, transparent 45%),
    linear-gradient(135deg, #f7f9fc, #ffffff);
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
  gap: 16px;
  color: #1f2d3d;
}

.auth-brand h1 {
  font-size: 32px;
  margin: 0;
}

.auth-brand p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.benefits {
  padding-left: 20px;
  margin: 12px 0 0;
  color: #409eff;
  line-height: 1.8;
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

.password-tips {
  margin-bottom: 16px;
}

.auth-submit {
  width: 100%;
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

