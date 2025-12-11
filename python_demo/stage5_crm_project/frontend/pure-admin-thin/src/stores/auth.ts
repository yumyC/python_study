import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { LoginForm, UserInfo } from '@/types/auth'
import { getToken, setToken, removeToken } from '@/utils/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string>('')
  const userInfo = ref<UserInfo | null>(null)
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!userInfo.value)

  // 登录
  const login = async (loginForm: LoginForm) => {
    loading.value = true
    try {
      const response = await authApi.login(loginForm)
      const { access_token, user } = response.data
      
      // 保存 token 和用户信息
      token.value = access_token
      userInfo.value = user
      setToken(access_token)
      
      return { success: true }
    } catch (error: any) {
      return { 
        success: false, 
        message: error.response?.data?.message || '登录失败' 
      }
    } finally {
      loading.value = false
    }
  }

  // 退出登录
  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('退出登录失败:', error)
    } finally {
      // 清除本地状态
      token.value = ''
      userInfo.value = null
      removeToken()
    }
  }

  // 获取用户信息
  const getUserInfo = async () => {
    try {
      const response = await authApi.getUserInfo()
      userInfo.value = response.data
      return response.data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  }

  // 检查认证状态
  const checkAuth = async () => {
    const savedToken = getToken()
    if (!savedToken) {
      return false
    }

    token.value = savedToken
    
    try {
      await getUserInfo()
      return true
    } catch (error) {
      // Token 无效，清除本地状态
      token.value = ''
      userInfo.value = null
      removeToken()
      return false
    }
  }

  // 刷新 Token
  const refreshToken = async () => {
    try {
      const response = await authApi.refreshToken()
      const { access_token } = response.data
      
      token.value = access_token
      setToken(access_token)
      
      return access_token
    } catch (error) {
      // 刷新失败，退出登录
      await logout()
      throw error
    }
  }

  return {
    // 状态
    token,
    userInfo,
    loading,
    
    // 计算属性
    isAuthenticated,
    
    // 方法
    login,
    logout,
    getUserInfo,
    checkAuth,
    refreshToken
  }
})