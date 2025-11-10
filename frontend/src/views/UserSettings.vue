<template>
  <div class="user-settings">
    <h1>用户设置 (User Settings)</h1>
    <p>管理你的帐户信息和外部服务集成。</p>

    <el-card class="setting-card" shadow="never">
      <template #header>
        <span>帐户信息</span>
      </template>
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
    </el-card>

    <el-card class="setting-card" shadow="never">
      <template #header>
        <span>服务集成</span>
      </template>
      
      <div v-if="googleConnected">
        <p>
          <el-icon color="green" style="vertical-align: middle;"><SuccessFilled /></el-icon>
          已连接到 Google Workspace (Gmail & Calendar)
        </p>
        <p>代理正在主动为你读取邮件和同步日历。</p>
        <el-button type="danger" @click="disconnectGoogle">
          断开连接
        </el-button>
      </div>

      <div v-else>
        <p>
          <el-icon color="red" style="vertical-align: middle;"><WarningFilled /></el-icon>
          未连接到 Google Workspace
        </p>
        <p>你需要授权访问你的 Gmail 和 Google 日历，以便 AI 代理为你工作。</p>
        <el-button type="primary" @click="connectGoogle">
          连接 Google 帐户 (模拟)
        </el-button>
      </div>
    </el-card>

  </div>
</template>

<script setup>
import { ref } from 'vue'
// 导入 Element Plus 图标
import { SuccessFilled, WarningFilled } from '@element-plus/icons-vue'

// 模拟当前登录的用户 (根据 proposal.pdf )
const user = ref({
  name: "Zhou Xinquan",
  id: "3036657562",
  role: "Front-End Team (Core Features UI)"
})

// 模拟 Google OAuth 连接状态
const googleConnected = ref(true)

// 模拟连接/断开连接的功能
const connectGoogle = () => {
  // 实际项目中：这里会触发 Xu Ziyi 负责的 OAuth 流程
  googleConnected.value = true
}

const disconnectGoogle = () => {
  googleConnected.value = false
}
</script>

<style scoped>
.user-settings {
  padding: 20px;
}
.setting-card {
  margin-top: 20px;
}
</style>