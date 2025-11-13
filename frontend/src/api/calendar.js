import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1', // 配合 vite proxy
  timeout: 10000
})

// 1. 获取待办事件列表 (GET /api/v1/calendar-events/)
export const getCalendarEvents = (params) => {
  return request.get('/calendar-events/', { params })
}

// 2. 确认事件 (POST /api/v1/calendar-events/{event_id}/confirm)
// 这个接口会把事件推送到 Google 日历并删除本地记录
export const confirmCalendarEvent = (eventId) => {
  return request.post(`/calendar-events/${eventId}/confirm`)
}

// 3. (可选) 创建事件 - 如果你想手动创建的话
export const createCalendarEvent = (data) => {
  return request.post('/calendar-events/', data)
}