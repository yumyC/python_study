<template>
  <div class="layout-container">
    <!-- 顶部导航栏 -->
    <div class="layout-header">
      <div class="header-left">
        <h1>CRM 管理系统</h1>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ userInfo?.full_name || userInfo?.username }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div class="layout-main">
      <!-- 侧边栏 -->
      <div class="layout-sidebar">
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          background-color="#001529"
          text-color="rgba(255, 255, 255, 0.65)"
          active-text-color="#fff"
          router
        >
          <template v-for="menu in menuList" :key="menu.path">
            <el-menu-item 
              v-if="!menu.children || menu.children.length === 0"
              :index="menu.path"
            >
              <el-icon v-if="menu.meta?.icon">
                <component :is="menu.meta.icon" />
              </el-icon>
              <span>{{ menu.meta?.title }}</span>
            </el-menu-item>
            
            <el-sub-menu v-else :index="menu.path">
              <template #title>
                <el-icon v-if="menu.meta?.icon">
                  <component :is="menu.meta.icon" />
                </el-icon>
                <span>{{ menu.meta?.title }}</span>
              </template>
              <el-menu-item
                v-for="child in menu.children"
                :key="child.path"
                :index="child.path"
              >
                <el-icon v-if="child.meta?.icon">
                  <component :is="child.meta.icon" />
                </el-icon>
                <span>{{ child.meta?.title }}</span>
              </el-menu-item>
            </el-sub-menu>
          </template>
        </el-menu>
      </div>

      <!-- 主内容区 -->
      <div class="layout-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { User, ArrowDown } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 用户信息
const userInfo = computed(() => authStore.userInfo)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 菜单列表（从路由配置中获取）
const menuList = computed(() => {
  const routes = router.getRoutes()
  const mainRoute = routes.find(r => r.path === '/')
  
  if (mainRoute?.children) {
    return mainRoute.children
      .filter(child => child.meta?.title && child.path !== 'dashboard')
      .map(child => ({
        path: `/${child.path}`,
        meta: child.meta,
        children: []
      }))
  }
  
  return []
})

// 处理下拉菜单命令
const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人信息功能开发中...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await authStore.logout()
        ElMessage.success('退出登录成功')
        router.push('/login')
      } catch (error) {
        // 用户取消操作
      }
      break
  }
}

onMounted(() => {
  // 确保用户信息已加载
  if (!userInfo.value) {
    authStore.getUserInfo()
  }
})
</script>

<style scoped>
.header-left h1 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}
</style>