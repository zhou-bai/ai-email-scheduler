<template>
  <div class="dashboard">
    <h1>我的仪表盘 (Dashboard)</h1>
    <p>AI已从你的邮件中提取了以下待处理事件和摘要。</p>

    <el-row :gutter="20">
      
      <el-col :span="14">
        <h2>邮件摘要 (Summaries)</h2>
        <div class="summary-list">
          <EmailSummary
            v-for="summary in emailSummaries"
            :key="summary.id"
            :summary="summary"
          />
        </div>
      </el-col>

      <el-col :span="10">
        <h2>待办事件 (Event Cards)</h2>
        <p v-if="pendingEvents.length === 0">没有待处理的事件。</p>
        
        <div class="event-list">
          <EventCard
            v-for="event in pendingEvents"
            :key="event.id"
            :event="event"
            style="margin-bottom: 20px;"
          />
        </div>
      </el-col>

    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
// 导入组件
import EventCard from '../components/EventCard.vue'
import EmailSummary from '../components/EmailSummary.vue'

// 导入模拟数据
import { mockEvents, mockSummaries } from '../data/mockData.js'

// 将模拟数据存入 ref
const pendingEvents = ref(mockEvents)
const emailSummaries = ref(mockSummaries)
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
/* 为摘要列表添加一个容器，以便未来可以滚动 */
.summary-list {
  border: 1px solid var(--el-border-color-light);
  border-radius: 4px;
}
</style>