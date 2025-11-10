<template>
  <el-container>
    <el-header>
      <el-menu mode="horizontal" :router="true">
        <el-menu-item index="/">Dashboard</el-menu-item>
        <el-menu-item index="/settings">User Settings</el-menu-item>
      </el-menu>
    </el-header>

    <el-main>
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<script setup>
// 这个布局组件不需要额外的脚本
</script>

<style>
/* 移除默认的 body 边距 */
body {
  margin: 0;
}
</style>