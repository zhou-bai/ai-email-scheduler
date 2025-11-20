<template>
  <el-container class="app-layout-top">
    
    <el-header v-if="!hideHeader" class="top-header">
      
      <div class="top-logo">
        <span>AI Email Scheduler</span>
      </div>

      <el-menu
        :default-active="activeRoute"
        :router="true"
        class="top-menu"
        mode="horizontal"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>UserSettings</span>
        </el-menu-item>
      </el-menu>

      <div class="user-info">
        <el-dropdown>
          <span class="el-dropdown-link">
            <el-avatar size="small" :icon="UserFilled" />
            <span class="username"> </span>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>Personal Center</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">
                Log Out
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-main
      :class="[
        'top-main-content',
        { 'no-header-content': hideHeader }
      ]"
    >
      <router-view></router-view>
    </el-main>

  </el-container>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HomeFilled, Setting, UserFilled } from '@element-plus/icons-vue'
import { getToken, logout as apiLogout } from './api'

const route = useRoute()
const router = useRouter()

const isAuthed = ref(Boolean(getToken()))

const handleAuthChange = () => {
  isAuthed.value = Boolean(getToken())
}

onMounted(() => {
  window.addEventListener('auth-change', handleAuthChange)
  handleAuthChange()
})

onUnmounted(() => {
  window.removeEventListener('auth-change', handleAuthChange)
})

const activeRoute = computed(() => route.path)
const hideHeader = computed(() => !isAuthed.value)

const handleLogout = async () => {
  try {
    await apiLogout()
  } catch {
    // ignore logout error
  } finally {
    router.push('/login')
  }
}
</script>

<style>
body {
  margin: 0;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}
.app-layout-top {
  min-height: 100vh;
}

.top-header {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;

  background-image: url('/top-background.jpg');
  background-size: cover;
  background-position: center top; 
  background-repeat: no-repeat;

  border-bottom: 3px solid rgba(255, 255, 255, 0.853);
}


.top-logo {
  width: 200px;
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  display: flex;
  align-items: center;
}

.top-menu {
  flex-grow: 1;
  border-bottom: none !important;
  background-color: transparent !important;
}
.top-menu .el-menu-item {
  color: #EAEAEA !important;
  background-color: transparent !important;
}
/* 悬停/激活时 */
.top-menu .el-menu-item:hover {
  color: #ffffff !important; 
  background-color: rgba(255, 255, 255, 0.1) !important; 
}
.top-menu .el-menu-item.is-active {
  color: #ffffff !important;
  border-bottom: 2px solid #ffffff !important;
}

.user-info {
  width: 200px;
  display: flex;
  justify-content: flex-end;
}
.user-info .el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
}
.user-info .username {
  margin-left: 8px;
  vertical-align: middle;
  color: #ffffff;
}

.top-main-content {
  background-color: #f0f2f5;
  padding: 0 !important;
}

.no-header-content {
  background: transparent;
  min-height: 100vh;
}
</style>