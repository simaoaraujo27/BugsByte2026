import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import UserInfo from '../components/UserInfo.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/profile',
    name: 'Profile',
    component: UserInfo
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router