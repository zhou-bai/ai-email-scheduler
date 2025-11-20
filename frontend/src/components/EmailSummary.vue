<template>
  <el-card class="summary-card" shadow="never">
    <div class="summary-content">
      <div class="summary-header">
        <div class="header-left">
          <span class="sender">{{ summary.sender }}</span>
          <span class="subject">{{ summary.subject }}</span>
        </div>
        <div class="header-right">
          <span class="time">{{ formatTime(summary.receivedAt) }}</span>
          <el-button
            type="danger"
            :icon="Delete"
            size="small"
            text
            @click="handleDelete"
            class="delete-btn"
          />
        </div>
      </div>
      <div class="summary-body">
        <p>{{ summary.summary }}</p>
      </div>
      <div class="summary-footer">
        <el-tag v-if="summary.hasEvent" type="warning" size="small">
          Includes schedule
        </el-tag>
      </div>
    </div>
  </el-card>
</template>

<script setup>
// 定义这个组件接收一个名为 'summary' 的 prop
import { Delete } from '@element-plus/icons-vue'

const props = defineProps({
  summary: {
    type: Object,
    required: true
  }
})

// 一个简单的时间格式化函数
const emit = defineEmits(['delete'])

const formatTime = (isoString) => {
  const date = new Date(isoString)
  return date.toLocaleString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const handleDelete = () => {
  emit('delete', props.summary.id)
}
</script>

<style scoped>
/* 移除卡片边框并添加底部边框 */
.summary-card {
  border: none;
  border-bottom: 1px solid var(--el-border-color-light);
  border-radius: 0;
}
/* 移除最后一张卡片的底部边框 */
.summary-card:last-child {
  border-bottom: none;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.sender {
  font-weight: bold;
  white-space: nowrap;
}

.subject {
  color: #606266;
  margin: 0 10px;
  /* 文本溢出显示省略号 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.time {
  color: #909399;
  font-size: 12px;
  white-space: nowrap; /* 防止时间换行 */
}

.delete-btn {
  padding: 4px;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.delete-btn:hover {
  opacity: 1;
}

.summary-body p {
  margin: 0 0 10px 0;
  color: #303133;
}
.summary-footer {
  text-align: left;
}
</style>