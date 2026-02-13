import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../components/LandingPage.vue'
import LoginPage from '../components/LoginPage.vue'
import UserInfo from '../components/UserInfo.vue'
import SiteHomePage from '../components/SiteHomePage.vue'
import ShopFinder from '../components/ShopFinder.vue'
import Negotiator from '../components/Negotiator.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: LandingPage
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
    path: '/dashboard',
    name: 'Dashboard',
    component: SiteHomePage
  },
  {
    path: '/shops',
    name: 'ShopFinder',
    component: ShopFinder
  },
  {
    path: '/negotiator',
    name: 'Negotiator',
    component: Negotiator
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
