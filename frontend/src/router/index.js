import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../components/LandingPage.vue'
import LoginPage from '../components/LoginPage.vue'
import UserInfo from '../components/UserInfo.vue'
import SiteHomePage from '../components/SiteHomePage.vue'
import AboutPage from '../components/AboutPage.vue'
import ForgotPassword from '../components/ForgotPassword.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: LandingPage
  },
  {
    path: '/about',
    name: 'About',
    component: AboutPage
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
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword
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
