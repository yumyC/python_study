import { request } from '@/utils/request'
import type { LoginForm, LoginResponse, RefreshTokenResponse, UserInfo } from '@/types/auth'

export const authApi = {
  // 登录
  login(data: LoginForm) {
    return request.post<LoginResponse>('/auth/login', data)
  },

  // 退出登录
  logout() {
    return request.post('/auth/logout')
  },

  // 获取用户信息
  getUserInfo() {
    return request.get<UserInfo>('/auth/me')
  },

  // 刷新 Token
  refreshToken() {
    return request.post<RefreshTokenResponse>('/auth/refresh')
  }
}