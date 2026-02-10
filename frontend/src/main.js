import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js'
import './assets/main.css'
import './assets/strategy-builder.css'

const app = createApp(App)
app.use(router)
app.mount('#app')
