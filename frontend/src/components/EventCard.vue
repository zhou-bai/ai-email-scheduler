<template>
  <el-card class="event-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="event-title" :title="event.title">{{ event.title }}</span>

        <div class="button-group">
          <el-button
            type="success"
            size="small"
            :loading="loading"
            @click="handleConfirm"
          >
            Confirm and synchronize
          </el-button>
          <el-button
            type="danger"
            size="small"
            :icon="Delete"
            :loading="deleting"
            @click="handleDelete"
          >
            Delete
          </el-button>
        </div>
      </div>
    </template>

    <el-descriptions :column="1" border>
      <el-descriptions-item label="Date">
        <el-tag>{{ event.date }}</el-tag>
      </el-descriptions-item>
      
      <el-descriptions-item label="Time">
        {{ event.time }}
      </el-descriptions-item>

      <el-descriptions-item label="Location">
        {{ event.location }}
      </el-descriptions-item>

      <el-descriptions-item label="Participants">
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { confirmCalendarEvent, deleteCalendarEvent } from '../api/calendar.js'

const props = defineProps({
  event: {
    type: Object,
    required: true
  }
})

// 定义 emits，用于通知父组件删除卡片
const emit = defineEmits(['confirmed', 'deleted'])

const loading = ref(false)
const deleting = ref(false)

const handleConfirm = async () => {
  loading.value = true
  try {
    // 调用后端 confirm 接口
    const res = await confirmCalendarEvent(props.event.id)

    if (res.data.success) {
      // 通知 Dashboard 组件移除这张卡片
      ElMessage.success(`Synced to Google Calendar (ID: ${res.data.google_event_id})`)
      emit('confirmed', props.event.id)
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('Sync failed, please try again')
  } finally {
    loading.value = false
  }
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to delete this calendar event?',
      'Delete Confirmation',
      {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )

    deleting.value = true
    await deleteCalendarEvent(props.event.id)
    ElMessage.success('Calendar event deleted successfully')
    emit('deleted', props.event.id)
  } catch (error) {
    if (error === 'cancel') return

    const errorMsg = error.response?.data?.detail
      || error.response?.data?.message
      || error.message
      || 'Failed to delete event'
    ElMessage.error(errorMsg)
  } finally {
    deleting.value = false
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
  max-width: 50%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.button-group {
  display: flex;
  gap: 8px;
}

.attendee-tag {
  margin-right: 5px;
}
</style>