import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 配置 NProgress
NProgress.configure({ showSpinner: false })

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/',
    redirect: '/dashboard',
    component: () => import('@/layout/index.vue'),
    meta: {
      requiresAuth: true
    },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: {
          title: '仪表盘',
          icon: 'Dashboard'
        }
      },
      {
        path: 'employees',
        name: 'Employees',
        component: () => import('@/views/employees/index.vue'),
        meta: {
          title: '员工管理',
          icon: 'User'
        }
      },
      {
        path: 'positions',
        name: 'Positions',
        component: () => import('@/views/positions/index.vue'),
        meta: {
          title: '岗位管理',
          icon: 'Briefcase'
        }
      },
      {
        path: 'menus',
        name: 'Menus',
        component: () => import('@/views/menus/index.vue'),
        meta: {
          title: '菜单管理',
          icon: 'Menu'
        }
      },
      {
        path: 'roles',
        name: 'Roles',
        component: () => import('@/views/roles/index.vue'),
        meta: {
          title: '角色管理',
          icon: 'UserFilled'
        }
      },
      {
        path: 'permissions',
        name: 'Permissions',
        component: () => import('@/views/permissions/index.vue'),
        meta: {
          title: '权限管理',
          icon: 'Lock'
        }
      },
      {
        path: 'work-logs',
        name: 'WorkLogs',
        component: () => import('@/views/work-logs/index.vue'),
        meta: {
          title: '工作日志',
          icon: 'Document'
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: {
      title: '页面不存在'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  const authStore = useAuthStore()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - CRM 管理系统` : 'CRM 管理系统'
  
  // 检查是否需要认证
  if (to.meta.requiresAuth !== false) {
    if (!authStore.isAuthenticated) {
      // 尝试从本地存储恢复登录状态
      await authStore.checkAuth()
      
      if (!authStore.isAuthenticated) {
        next('/login')
        return
      }
    }
  }
  
  // 如果已登录用户访问登录页，重定向到首页
  if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
    return
  }
  
  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router