import { createRouter, createWebHistory } from 'vue-router'
// 导入你的 Dashboard 视图
import Dashboard from '../views/Dashboard.vue'
import AuthCallback from '../views/AuthCallback.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/settings',
    name: 'UserSettings',
    // 这是你负责的另一个页面，我们用“懒加载” 
    component: () => import('../views/UserSettings.vue')
  },
  {
    path: '/auth/callback', // 必须和后端 oauth.py 里的 success_path 对应
    name: 'AuthCallback',
    component: AuthCallback
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router