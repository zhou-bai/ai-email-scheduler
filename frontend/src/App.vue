<template>
  <el-container class="app-layout-top">
    
    <el-header class="top-header">
      
      <div class="top-logo">
        <span>AI 助手</span>
      </div>

      <el-menu
        :default-active="activeRoute"
        :router="true"
        class="top-menu"
        mode="horizontal"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>用户设置</span>
        </el-menu-item>
      </el-menu>

      <div class="user-info">
        <el-dropdown>
          <span class="el-dropdown-link">
            <el-avatar size="small" :icon="UserFilled" />
            <span class="username"> 周新泉 (Chow)</span>
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

.top-main-content {
  background-color: #f0f2f5;
  padding: 0 !important; /* 强制移除内边距 */
}

.app-layout-top {
  min-height: 100vh;
}

/* 1. 顶部 Header 样式 */
.top-header {
  height: 60px;
  display: flex;
  align-items: center;
  background-color: #fff; /* 顶部导航为白色 */
  border-bottom: 1px solid #d8dce5;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  padding: 0 20px;
}
.top-logo {
  width: 200px; /* Logo 区域宽度 */
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
}
.top-menu {
  flex-grow: 1; /* 菜单占据中间所有剩余空间 */
  border-bottom: none; /* 移除 el-menu 默认的底边框 */
}
.user-info {
  width: 200px; /* 用户信息区域宽度 */
  display: flex;
  justify-content: flex-end; /* 靠右对齐 */
}
.user-info .el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
}
.user-info .username {
  margin-left: 8px;
  vertical-align: middle;
}

/* 2. 主内容区样式 */
.top-main-content {
  /* !!重要!! 
    设置统一的浅灰色背景。
    这个颜色会成为所有页面的“底色”。
  */
  background-color: #f0f2f5;
  /* 我们在这里设置全局 padding，
    所以页面本身就不需要 padding 了。
  */
  padding: 24px;
}
</style>