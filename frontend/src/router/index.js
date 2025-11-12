import { createRouter, createWebHistory } from 'vue-router'
// 导入你的 Dashboard 视图
import Dashboard from '../views/Dashboard.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/settings',
    name: 'UserSettings',
    // 这是你负责的另一个页面，我们用“懒加载” 
    component: () => import('../views/UserSettings.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const isAuthenticated = Boolean(localStorage.getItem('authToken'))

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({
      path: '/login',
      query: to.fullPath ? { redirect: to.fullPath } : undefined
    })
    return
  }

  if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    next(to.query.redirect || '/')
    return
  }

  next()
})

export default router