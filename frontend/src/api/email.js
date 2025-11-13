import axios from 'axios'

// 创建一个 axios 实例
const request = axios.create({
  baseURL: '', // 因为配置了 proxy，这里留空或者是 '/api/v1' 均可，建议留空靠 proxy 转发
  timeout: 5000
})

// 1. 获取所有邮件列表
export const getEmails = (params) => {
  return request.get('/api/v1/emails/', { params })
}

// 2. 触发 AI 处理邮件
export const processEmails = () => {
  return request.post('/api/v1/emails/process', {
    max_results: 10
  })
}

// 3. 删除邮件
export const deleteEmail = (emailId) => {
  return request.delete(`/api/v1/emails/${emailId}`)
}