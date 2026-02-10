import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: () => import('./views/LandingPage.vue'),
  },
  {
    path: '/app',
    name: 'backtest-app',
    component: () => import('./views/BacktestApp.vue'),
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
