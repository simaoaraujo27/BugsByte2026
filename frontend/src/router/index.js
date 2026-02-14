import { createRouter, createWebHistory } from 'vue-router'
import { auth } from '../auth'

import LandingPage from '../components/LandingPage.vue'
import LoginPage from '../components/LoginPage.vue'
import UserInfo from '../components/UserInfo.vue'
import SiteHomePage from '../components/SiteHomePage.vue'
import AboutPage from '../components/AboutPage.vue'
import ForgotPassword from '../components/ForgotPassword.vue'
import ResetPassword from '../components/ResetPassword.vue'
import FavoritesPage from '../components/FavoritesPage.vue'

const routes = [
  { path: '/', name: 'Landing', component: LandingPage },
  { path: '/about', name: 'About', component: AboutPage },
  { path: '/signup', name: 'SignUp', component: UserInfo },
  { path: '/login', name: 'Login', component: LoginPage },
  { path: '/forgot-password', name: 'ForgotPassword', component: ForgotPassword },
  { path: '/reset-password', name: 'ResetPassword', component: ResetPassword },
  { 
    path: '/dashboard', 
    name: 'Dashboard', 
    component: SiteHomePage, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/dashboard/:section', 
    name: 'DashboardSection', 
    component: SiteHomePage, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/dashboard/:section/:subsection', 
    name: 'DashboardSubsection', 
    component: SiteHomePage, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/favorites', 
    name: 'Favorites', 
    component: FavoritesPage, 
    meta: { requiresAuth: true } 
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthPage = to.path === '/login' || to.path === '/signup'
  
  // Use the new async verification
  const loggedIn = await auth.checkAuth()

  if (requiresAuth && !loggedIn) {
    next('/login')
  } else if (loggedIn && isAuthPage) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router