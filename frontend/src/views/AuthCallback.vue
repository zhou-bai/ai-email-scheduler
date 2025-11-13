<template>
  <div class="callback-container" v-loading="true" element-loading-text="正在处理 Google 授权...">
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

onMounted(() => {
  console.log('Callback URL:', window.location.href) // 方便调试，看控制台打印的真实链接

  let token = null
  let userId = null
  let email = null

  // 1. 优先尝试从 Hash (#) 中解析 (对应后端目前的写法)
  if (route.hash) {
    // route.hash 是类似 "#token=xxx&user_id=1..." 的字符串
    const hashStr = route.hash.substring(1) // 去掉开头的 #
    const params = new URLSearchParams(hashStr)
    token = params.get('token')
    userId = params.get('user_id')
    email = params.get('email')
  }

  // 2. 如果 Hash 里没有，再尝试从 Query (?) 中解析 (作为备选)
  if (!token && route.query.token) {
    token = route.query.token
    userId = route.query.user_id
    email = route.query.email
  }

  // 3. 验证并保存
  if (token) {
    // 保存到本地
    localStorage.setItem('token', token)
    if (userId) localStorage.setItem('user_id', userId)
    if (email) localStorage.setItem('user_email', email)

    ElMessage.success('Google 账号连接成功！')
    
    // 跳转回首页
    router.push('/')
  } else {
    console.error('未找到 Token。Hash:', route.hash, 'Query:', route.query)
    ElMessage.error('授权失败：未收到 Token')
    // 建议注释掉下面这行，留在当前页方便看 Console 里的报错信息
    // router.push('/login') 
  }
})
</script>

<style scoped>
.callback-container {
  height: 100vh;
  width: 100vw;
}
</style>