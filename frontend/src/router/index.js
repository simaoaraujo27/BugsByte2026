import { createRouter, createWebHistory } from 'vue-router'
import { auth } from '../auth'

// Lazy load components for better reliability
const LandingPage = () => import('../components/LandingPage.vue')
const LoginPage = () => import('../components/LoginPage.vue')
const UserInfo = () => import('../components/UserInfo.vue')
const SiteHomePage = () => import('../components/SiteHomePage.vue')
const AboutPage = () => import('../components/AboutPage.vue')
const ForgotPassword = () => import('../components/ForgotPassword.vue')
const ResetPassword = () => import('../components/ResetPassword.vue')
const FavoritesPage = () => import('../components/FavoritesPage.vue')

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

router.beforeEach((to, from, next) => {
  const loggedIn = auth.isLoggedIn()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !loggedIn) {
    next('/login')
  } else if (loggedIn && (to.path === '/login' || to.path === '/signup')) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router