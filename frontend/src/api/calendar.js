// src/api/calendar.js
import axios from 'axios'

const request = axios.create({
  baseURL: '', 
  timeout: 10000
})

// 拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// --- API 定义 ---

export const getCalendarEvents = (params) => {
  return request.get('/api/v1/calendar-events/', { params })
}

export const confirmCalendarEvent = (eventId) => {
  return request.post(`/api/v1/calendar-events/${eventId}/confirm`)
}

export const createCalendarEvent = (data) => {
  return request.post('/api/v1/calendar-events/', data)
}

export default request