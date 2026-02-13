import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../components/LandingPage.vue'
import LoginPage from '../components/LoginPage.vue'
import SiteHomePage from '../components/SiteHomePage.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: LandingPage
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: SiteHomePage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
