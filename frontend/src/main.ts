import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import {Histogram} from "@element-plus/icons-vue";

// 配置axios默认值
axios.defaults.baseURL = 'http://localhost:6565'
axios.defaults.headers.common['Content-Type'] = 'application/json'
axios.defaults.withCredentials = false  // 改为false

// 添加请求拦截器
axios.interceptors.request.use(
  config => {
    console.log('Sending request:', config)
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 添加响应拦截器
axios.interceptors.response.use(
  response => {
    console.log('Received response:', response)
    return response
  },
  error => {
    console.error('Response error:', error)
    const errorMsg = error.response?.data?.error || '操作失败，请稍后重试'
    ElMessage.error(errorMsg)
    return Promise.reject(error)
  }
)

const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.component('Histogram', Histogram);
app.mount('#app') 