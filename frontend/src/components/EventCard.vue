<template>
  <el-card class="event-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="event-title" :title="event.title">{{ event.title }}</span>
        
        <el-button 
          type="success" 
          size="small"
          :loading="loading"
          @click="handleConfirm"
        >
          确认并同步
        </el-button>
      </div>
    </template>

    <el-descriptions :column="1" border>
      <el-descriptions-item label="日期">
        <el-tag>{{ event.date }}</el-tag>
      </el-descriptions-item>
      
      <el-descriptions-item label="时间">
        {{ event.time }}
      </el-descriptions-item>

      <el-descriptions-item label="地点">
        {{ event.location }}
      </el-descriptions-item>

      <el-descriptions-item label="参会者">
        <el-tag 
          v-for="(person, index) in event.attendees" 
          :key="index" 
          type="info" 
          size="small" 
          class="attendee-tag"
        >
          {{ person }}
        </el-tag>
      </el-descriptions-item>
    </el-descriptions>

  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { confirmCalendarEvent } from '../api/calendar.js'

const props = defineProps({
  event: {
    type: Object,
    required: true
  }
})

// 定义 emits，用于通知父组件删除卡片
const emit = defineEmits(['confirmed'])

const loading = ref(false)

const handleConfirm = async () => {
  loading.value = true
  try {
    // 调用后端 confirm 接口
    const res = await confirmCalendarEvent(props.event.id)
    
    if (res.data.success) {
      ElMessage.success(`已同步至 Google Calendar (ID: ${res.data.google_event_id})`)
      // 通知 Dashboard 组件移除这张卡片
      emit('confirmed', props.event.id)
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('同步失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.event-title {
  font-weight: bold;
  /* 简单的文本截断 */
  max-width: 60%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.attendee-tag {
  margin-right: 5px;
}
</style>