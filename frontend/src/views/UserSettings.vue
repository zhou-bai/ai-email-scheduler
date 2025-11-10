<template>
  <div class="user-settings">
    
    <el-page-header :icon="null">
      <template #title>
        <strong>用户设置</strong>
      </template>
      <template #content>
        <span class="text-large font-600 mr-3"> 管理你的帐户信息和外部服务 </span>
      </template>
    </el-page-header>

    <el-divider />

    <el-card class="settings-container">
      
      <el-divider content-position="left"><h3>帐户信息</h3></el-divider>
      
      <el-descriptions :column="1" border>
        <el-descriptions-item label="用户名">
          {{ user.name }} (你)
        </el-descriptions-item>
        <el-descriptions-item label="用户ID (来自提案)">
          {{ user.id }}
        </el-descriptions-item>
        <el-descriptions-item label="团队角色">
          {{ user.role }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left"><h3>服务集成</h3></el-divider>
      
      <div v-if="googleConnected" class="integration-status">
        <el-icon color="#67C23A" :size="20" style="vertical-align: middle; margin-right: 8px;">
          <SuccessFilled />
        </el-icon>
        <strong>已连接到 Google Workspace (Gmail & Calendar)</strong>
        <p class="status-desc">
          代理正在主动为你读取邮件和同步日历。
        </p>
        <el-button type="danger" @click="disconnectGoogle">
          断开连接
        </el-button>
      </div>

      <div v-else class="integration-status">
        <el-icon color="#F56C6C" :size="20" style="vertical-align: middle; margin-right: 8px;">
          <WarningFilled />
        </el-icon>
        <strong>未连接到 Google Workspace</strong>
        <p class="status-desc">
          你需要授权访问你的 Gmail 和 Google 日历，以便 AI 代理为你工作。
        </p>
        <el-button type="primary" @click="connectGoogle">
          连接 Google 帐户 (模拟)
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