import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

const app = createApp(App)

// 配置全局 Axios 默认值
axios.defaults.baseURL = 'http://localhost:8002'

app.use(router)
app.use(store)
app.mount('#app') 