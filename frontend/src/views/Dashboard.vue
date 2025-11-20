<template>
  <div class="dashboard">
    <el-page-header :icon="null">
      <template #title>
        <strong>Dashboard</strong>
      </template>
      <template #content>
        <span class="text-large font-600 mr-3"> AI Assistant Activity Center </span>
      </template>
      <template #extra>
      <el-button type="warning" @click="connectGoogle">
        <el-icon><Link /></el-icon> Connect your Google account
      </el-button>
      
      <el-button type="primary" :icon="Refresh" circle @click="handleRefresh" />
    </template>
    </el-page-header>

    <el-divider />

    <el-tabs v-model="activeView" type="border-card" class="dashboard-tabs">
      <el-tab-pane name="summaries">
        <template #label>
          <span class="tab-label">
            <el-icon><Message /></el-icon>
            <span>Email Summary</span>
            <el-badge :value="emailSummaries.length" class="tab-badge" />
          </span>
        </template>
        <el-empty v-if="emailSummaries.length === 0" description="No email data available." :image-size="100" />
        <div v-else class="summary-list-container">
          <EmailSummary v-for="summary in emailSummaries" :key="summary.id" :summary="summary" />
        </div>
      </el-tab-pane>

      <el-tab-pane name="events">
        <template #label>
          <span class="tab-label">
            <el-icon><Calendar /></el-icon>
            <span>To-do</span>
            <el-badge :value="pendingEvents.length" type="warning" class="tab-badge" />
          </span>
        </template>
        
        <el-empty v-if="pendingEvents.length === 0" description="No pending events" :image-size="100" />

        <div v-else class="event-list-container">
          <el-row :gutter="20">
            <el-col
              v-for="event in pendingEvents"
              :key="event.id"
              :xs="24" :sm="12" :md="8"
              style="margin-bottom: 20px;"
            >
              <EventCard 
                :event="event" 
                @confirmed="removeEventFromList"
              />
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <el-tab-pane name="compose">
        <template #label>
          <span class="tab-label">
            <el-icon><EditPen /></el-icon>
            <span>Generate email</span>
          </span>
        </template>

        <GenerateEmail />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import EventCard from '../components/EventCard.vue'
import EmailSummary from '../components/EmailSummary.vue'
import GenerateEmail from '../components/GenerateEmail.vue'
import { Refresh, Message, Calendar, EditPen } from '@element-plus/icons-vue'


// 引入 API
import { getEmails, processEmails } from '../api/email.js'
import { getCalendarEvents } from '../api/calendar.js'
import { getGoogleAuthUrl } from '../api/auth.js'


const activeView = ref('summaries')
const loading = ref(false)
const pendingEvents = ref([])
const emailSummaries = ref([])

// 辅助函数：从 ISO 时间字符串提取日期和时间
const parseDateTime = (isoStr) => {
  if (!isoStr) return { date: 'N/A', time: 'N/A' }
  const d = new Date(isoStr)
  return {
    date: d.toLocaleDateString(),
    time: d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
}

// 获取所有数据
const fetchData = async () => {
  try {
    // 1. 获取邮件
    const emailRes = await getEmails({ limit: 20 })
    emailSummaries.value = emailRes.data.map(item => ({
      id: item.id,
      sender: item.from_address,
      subject: item.subject,
      summary: item.snippet || item.body_text,
      receivedAt: item.received_at,
      hasEvent: false 
    }))

    // 2. 获取待办事件 (新增)
    const eventRes = await getCalendarEvents({ limit: 50 })
    
    // 数据映射：Backend -> Frontend Component
    pendingEvents.value = eventRes.data.map(evt => {
      const { date, time } = parseDateTime(evt.start_time)
      return {
        id: evt.id,          // 必须保留 ID 用于确认接口
        title: evt.summary,  // 映射 summary -> title
        location: evt.location || '线上 / 未定',
        attendees: evt.attendees ? [evt.attendees] : [], // 后端是字符串，前端v-for需要数组
        date: date,
        time: time,
        rawStartTime: evt.start_time,
        rawEndTime: evt.end_time
      }
    })

  } catch (error) {
    console.error('数据加载失败:', error)
    ElMessage.error('获取数据失败')
  }
}

const handleRefresh = async () => {
  loading.value = true
  try {
    const res = await processEmails() // 触发 AI 分析
    if (res.data.success) {
      ElMessage.success(`分析完成，生成了 ${res.data.created_events_count} 个新事件`)
      await fetchData() // 重新拉取最新数据
    } else {
      ElMessage.warning('处理未完全成功')
    }
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}

// 当用户在 EventCard 点击确认后，前端直接把该条目移除，无需刷新整个列表
const removeEventFromList = (id) => {
  pendingEvents.value = pendingEvents.value.filter(e => e.id !== id)
}

const connectGoogle = async () => {
  try {
    // 1. 请求后端，拿到 Google 的授权页面 URL
    const res = await getGoogleAuthUrl()
    const authUrl = res.data.auth_url
    
    // 2. 让浏览器直接跳转到 Google
    window.location.href = authUrl
  } catch (error) {
    console.error('无法获取授权链接', error)
    ElMessage.error('无法连接至 Google')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
/* 保持你的样式不变 */
.dashboard {
  background-image: url('/my-background.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  padding: 24px;
  min-height: calc(100vh - 60px);
  box-sizing: border-box;
}
.dashboard-tabs {
  min-height: 500px;
  opacity: 0.95;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  overflow: hidden; 
}
.tab-label { display: flex; align-items: center; gap: 8px; }
.tab-badge { margin-left: 8px; }
:deep(.el-page-header__title strong) { color: #ffffff; }
:deep(.el-page-header__content span) { color: #ffffff; }
</style>