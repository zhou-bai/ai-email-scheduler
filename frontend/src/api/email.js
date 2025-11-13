// src/api/email.js
import axios from 'axios'

// 1. 创建实例 (baseURL 留空或写 /api/v1 均可，这里留空配合 proxy)
const request = axios.create({
  baseURL: '', 
  timeout: 10000
  // 注意：这里不再写死 headers
})

// 2. 【关键】恢复请求拦截器
// 它的作用是：每次发请求前，去浏览器本地存储里拿最新的 Token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      // 必须加上 Bearer 前缀
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)


// --- API 定义 ---

export const getEmails = (params) => {
  return request.get('/api/v1/emails/', { params })
}

export const processEmails = () => {
  return request.post('/api/v1/emails/process', {
    max_results: 10
  })
}

export const deleteEmail = (emailId) => {
  return request.delete(`/api/v1/emails/${emailId}`)
}

// 记得导出默认实例，供 auth.js 使用
export default request