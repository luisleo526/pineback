import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js'
import './assets/main.css'
import './assets/strategy-builder.css'

const app = createApp(App)

// Global error handler to catch silent failures
app.config.errorHandler = (err, instance, info) => {
  console.error('[Vue Error]', err, info)
}

router.onError((err) => {
  console.error('[Router Error]', err)
})

app.use(router)
app.mount('#app')
