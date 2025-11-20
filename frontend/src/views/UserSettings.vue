<template>
  <div class="user-settings">
    
    <el-page-header :icon="null">
      <template #title>
        <strong>User Settings</strong>
      </template>
      <template #content>
        <span class="text-large font-600 mr-3"> Manage your account information and external services </span>
      </template>
    </el-page-header>

    <el-divider />

    <el-card class="settings-container">
      
      <el-divider content-position="left"><h3>Account Information</h3></el-divider>
      
      <el-descriptions :column="1" border>
        <el-descriptions-item label="User Name">
          {{ user.name }} (You)
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left"><h3>Service Integration</h3></el-divider>
      
      <div v-if="googleConnected" class="integration-status">
        <el-icon color="#67C23A" :size="20" style="vertical-align: middle; margin-right: 8px;">
          <SuccessFilled />
        </el-icon>
        <strong>Connected to Google Workspace (Gmail & Calendar)</strong>
        <p class="status-desc">
          The agent is proactively reading your emails and syncing your calendar.
        </p>
        <el-button type="danger" @click="disconnectGoogle">
          Disconnect
        </el-button>
      </div>

      <div v-else class="integration-status">
        <el-icon color="#F56C6C" :size="20" style="vertical-align: middle; margin-right: 8px;">
          <WarningFilled />
        </el-icon>
        <strong>Not connected to Google Workspace</strong>
        <p class="status-desc">
          You need to grant access to your Gmail and Google Calendar so that the AI ​​agent can work for you.
        </p>
        <el-button type="primary" @click="connectGoogle">
          Connect your Google account
        </el-button>
      </div>

    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { SuccessFilled, WarningFilled } from '@element-plus/icons-vue'

// 模拟当前登录的用户 (根据 proposal.pdf)
const user = ref({
  name: "Zhou",
  id: "30366",
  role: "Front-End Team (Core Features UI)"
})

// 模拟 Google OAuth 连接状态
const googleConnected = ref(true)

const connectGoogle = () => {
  googleConnected.value = true
}

const disconnectGoogle = () => {
  googleConnected.value = false
}
</script>

<style scoped>
/* 1. 添加背景图片 (与 Dashboard 一致) 
*/
.user-settings {
  padding: 24px;
  min-height: calc(100vh - 60px); /* 100vh - 顶部导航栏高度 */
  box-sizing: border-box; /* 确保 padding 不会撑破高度 */

  /* --- 新增 (与 Dashboard 相同) --- */
  background-image: url('/my-background.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

/* 2. 修复字体颜色 (与 Dashboard 一致) 
  (如果背景图片是深色，必须将标题改为白色)
*/
:deep(.el-page-header__title strong) {
  color: #ffffff;
}
:deep(.el-page-header__content span) {
  color: #ffffff;
}

/* 3. 设置内容卡片的透明度 (与 Dashboard 一致) 
*/
.settings-container {
  max-width: 1000px; /* 限制最大宽度，提高可读性 */
  margin: 0 auto; /* 在大屏幕上居中显示 */
  border-radius: 12px;
  overflow: hidden; /* 确保内部也遵循圆角 */

  /* --- 新增/确认 (与 Dashboard 相同) --- */
  opacity: 0.9;
}

.user-settings {
  padding: 24px;
  min-height: calc(100vh - 60px); /* 100vh - 顶部导航栏高度 */
  box-sizing: border-box; /* 确保 padding 不会撑破高度 */
}

/* 2. 美化页面: 
  设置主容器卡片的样式
*/
.settings-container {
  max-width: 1000px; /* 限制最大宽度，提高可读性 */
  margin: 0 auto; /* 在大屏幕上居中显示 */
  
  /* 与 Dashboard 上的 tabs 样式保持一致 */
  border-radius: 12px;
  opacity: 0.97;
  overflow: hidden; /* 确保内部也遵循圆角 */
}

/* 3. 美化分区标题 */
.el-divider h3 {
  margin: 0;
  font-weight: 600;
  color: #303133;
}

/* 4. 美化集成状态区域 */
.integration-status {
  padding-left: 10px;
}
.status-desc {
  font-size: 14px;
  color: #606266;
  margin-top: 10px;
}
</style>