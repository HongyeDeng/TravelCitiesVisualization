import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import 'leaflet/dist/leaflet.css'
import {createPinia} from 'pinia'

const pinia = createPinia()
const app = createApp(App).use(router)
app.use(Antd)
app.use(pinia)
app.mount('#app')

