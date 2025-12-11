// 登录表单
export interface LoginForm {
  username: string
  password: string
}

// 用户信息
export interface UserInfo {
  id: string
  username: string
  email: string
  full_name: string
  position?: {
    id: string
    name: string
    code: string
  }
  role?: {
    id: string
    name: string
    code: string
  }
  status: 'active' | 'inactive'
  created_at: string
  updated_at: string
}

// 登录响应
export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: UserInfo
}

// Token 刷新响应
export interface RefreshTokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}