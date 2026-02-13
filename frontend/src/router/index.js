import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import UserInfo from '../components/UserInfo.vue'
import LoginPage from '../components/LoginPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/signup',
    name: 'SignUp',
    component: UserInfo
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
