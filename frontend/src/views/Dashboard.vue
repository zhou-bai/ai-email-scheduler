<template>
  <div class="dashboard">
    <el-page-header :icon="null">
      <template #title>
        <strong>仪表盘</strong>
      </template>
      <template #content>
        <span class="text-large font-600 mr-3"> AI 助手活动中心 </span>
      </template>
      <template #extra>
        <el-button type="primary" :icon="Refresh" circle @click="refreshData" />
      </template>
    </el-page-header>

    <el-divider />

    <el-tabs v-model="activeView" type="border-card" class="dashboard-tabs">

      <el-tab-pane name="summaries">
        <template #label>
          <span class="tab-label">
            <el-icon><Message /></el-icon>
            <span>邮件摘要</span>
            <el-badge :value="emailSummaries.length" class="tab-badge" />
          </span>
        </template>

        <el-empty 
          v-if="emailSummaries.length === 0" 
          description="暂无邮件摘要" 
          :image-size="100" 
        />
        
        <div v-else class="summary-list-container">
          <EmailSummary
            v-for="summary in emailSummaries"
            :key="summary.id"
            :summary="summary"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane name="events">
        <template #label>
          <span class="tab-label">
            <el-icon><Calendar /></el-icon>
            <span>待办事件</span>
            <el-badge :value="pendingEvents.length" type="warning" class="tab-badge" />
          </span>
        </template>
        
        <el-empty 
          v-if="pendingEvents.length === 0" 
          description="暂无待办事件" 
          :image-size="100"
        />

        <div v-else class="event-list-container">
          <el-row :gutter="20">
            <el-col
              v-for="event in pendingEvents"
              :key="event.id"
              :xs="24" :sm="12" :md="8"
              style="margin-bottom: 20px;"
            >
              <EventCard :event="event" />
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

    </el-tabs>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import EventCard from '../components/EventCard.vue'
import EmailSummary from '../components/EmailSummary.vue'
import { mockEvents, mockSummaries } from '../data/mockData.js'
import { Refresh, Message, Calendar } from '@element-plus/icons-vue'

// 新增: 用于控制当前激活的标签页
const activeView = ref('summaries') // 默认显示“邮件摘要”

const pendingEvents = ref(mockEvents)
const emailSummaries = ref(mockSummaries)

const refreshData = () => {
  alert('（模拟）正在刷新数据...')
}

</script>

<style scoped>
.dashboard {
  /* 使用 /my-background.jpg 
    (Vite 会自动将其解析为 public 文件夹中的文件) 
  */
  background-image: url('/my-background.jpg');
  
  /* 确保图片覆盖整个区域 */
  background-size: cover;
  
  /* 图片居中显示 */
  background-position: center;
  
  /* 防止图片平铺 */
  background-repeat: no-repeat;
  
  /* !!重要!! 
    我们之前在 App.vue 中设置了全局 padding，
    但由于 .dashboard 现在是 router-view 的根元素，
    我们需要自己在这里重新声明 padding。
  */
  padding: 24px;
  
  /* 确保它至少填满内容区的高度 
    (100vh - 60px 顶部导航栏高度)
  */
  min-height: calc(100vh - 60px);
  box-sizing: border-box; /* 确保 padding 不会撑破高度 */
}

/* 你之前为 .dashboard-tabs 添加的透明度
  现在会产生“毛玻璃”效果，透出背景图片！
*/
.dashboard-tabs {
  min-height: 500px;
  opacity: 0.9;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);

  /* 新增: 圆角 */
  border-radius: 12px;

  overflow: hidden; 
}

/* 标签页标题样式 */
.tab-label {
  display: flex;
  align-items: center;
  gap: 8px; /* 图标和文字的间距 */
}
.tab-badge {
  margin-left: 8px;
}

/* 摘要列表容器 (移除边框，因为tabs已有) */
.summary-list-container {
  /* 之前在EmailSummary.vue中设置了边框，这里不需要额外样式 */
}

:deep(.el-page-header__title strong) {
  color: #ffffff; /* 仪表盘 -> 白色 */
}

/* 使用 :deep() 穿透 el-page-header 组件，
  将其内部 content 插槽中的 span 标签字体变为白色
*/
:deep(.el-page-header__content span) {
  color: #ffffff; /* AI助手活动中心 -> 白色 */
}
</style>