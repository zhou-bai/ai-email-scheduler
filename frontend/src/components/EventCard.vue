<template>
  <el-card class="event-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span>{{ event.title }}</span>
        <el-button type="primary" size="small">
          确认并添加到日历
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
        <el-tag v-for="person in event.attendees" :key="person" type="info" size="small" class="attendee-tag">
          {{ person }}
        </el-tag>
      </el-descriptions-item>
    </el-descriptions>

  </el-card>
</template>

<script setup>
// 定义这个组件接收一个名为 'event' 的 prop
defineProps({
  event: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.attendee-tag {
  margin-right: 5px;
}
</style>