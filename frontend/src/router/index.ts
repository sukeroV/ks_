import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Layout from '../components/Layout.vue'
import Home from '../views/Home.vue'
import Profile from '../views/Profile.vue'
import Practice from '../views/Practice.vue'
import History from '../views/History.vue'
import Mistakes from '../views/Mistakes.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/register',
      name: 'Register',
      component: Register
    },
    {
      path: '/',
      component: Layout,
      children: [
        {
          path: 'home',
          name: 'Home',
          component: Home,
          meta: { requiresAuth: true }
        },
        {
          path: 'practice',
          name: 'Practice',
          component: Practice,
          meta: { requiresAuth: true }
        },
        {
          path: 'practice/:id',
          name: 'PracticeDetail',
          component: () => import('../views/PracticeDetail.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: 'history',
          name: 'History',
          component: History,
          meta: { requiresAuth: true }
        },
        {
          path: 'mistakes',
          name: 'Mistakes',
          component: Mistakes,
          meta: { requiresAuth: true }
        },
        {
          path: 'profile',
          name: 'Profile',
          component: Profile,
          meta: { requiresAuth: true }
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('user')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router 