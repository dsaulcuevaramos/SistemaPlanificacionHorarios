
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import './assets/css/variables.css'
import './assets/css/layout.css'

const app = createApp(App)

app.use(createPinia())  // Para poder usar pinia
app.use(router)         // <--- IMPORTANTE: Conectar el router
app.mount('#app')


