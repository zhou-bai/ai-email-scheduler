import { createApp } from 'vue'

// 导入 Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 导入你的路由
import router from './router'

import App from './App.vue'

const app = createApp(App)

app.use(ElementPlus) // 使用 Element Plus
app.use(router)      // 使用 Vue Router

app.mount('#app')