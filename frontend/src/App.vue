<template>
  <el-container class="app-layout-top">
    
    <el-header class="top-header">
      
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
            <span class="username"> 周</span>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>个人中心</el-dropdown-item>
              <el-dropdown-item divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-main class="top-main-content">
      <router-view></router-view>
    </el-main>

  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
// 确保所有图标都已导入
import { HomeFilled, Setting, UserFilled, Cpu } from '@element-plus/icons-vue'

const route = useRoute()
const activeRoute = computed(() => route.path)
</script>

<style>
body {
  margin: 0;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}
.app-layout-top {
  min-height: 100vh;
}

/* 1. 顶部 Header 样式 (应用背景图) */
.top-header {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;

  /* --- 新增：添加背景图片 --- */
  background-image: url('/top-background.jpg');
  background-size: cover;
  /* (让导航栏的背景图和页面背景图在顶部对齐) */
  background-position: center top; 
  background-repeat: no-repeat;

  border-bottom: 3px solid rgba(255, 255, 255, 0.853);
}

/* 2. Logo 样式 (字体改白) */
.top-logo {
  width: 200px;
  font-size: 20px;
  font-weight: 600;
  color: #ffffff; /* <-- 改为白色 */
  display: flex;
  align-items: center;
}

/* 3. 菜单样式 (背景透明，字体改白) */
.top-menu {
  flex-grow: 1;
  border-bottom: none !important;
  background-color: transparent !important; /* <-- 透明背景 */
}
/* 覆盖 el-menu 的字体颜色 */
.top-menu .el-menu-item {
  color: #EAEAEA !important; /* <-- 浅白色 */
  background-color: transparent !important;
}
/* 悬停/激活时 */
.top-menu .el-menu-item:hover {
  color: #ffffff !important; /* <-- 纯白 */
  background-color: rgba(255, 255, 255, 0.1) !important; /* <-- 轻微提亮 */
}
.top-menu .el-menu-item.is-active {
  color: #ffffff !important; /* <-- 纯白 */
  border-bottom: 2px solid #ffffff !important; /* <-- 白色下划线 */
}

/* 4. 用户信息 (字体改白) */
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
  color: #ffffff; /* <-- 改为白色 */
}

/* 5. 主内容区 (移除 padding) */
.top-main-content {
  background-color: #f0f2f5;
  padding: 0 !important; /* 保持为0，由子页面管理 */
}
</style>