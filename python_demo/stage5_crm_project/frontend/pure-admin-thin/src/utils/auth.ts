import Cookies from 'js-cookie'

const TOKEN_KEY = 'crm_token'

// 获取 Token
export function getToken(): string | undefined {
  return Cookies.get(TOKEN_KEY)
}

// 设置 Token
export function setToken(token: string): void {
  Cookies.set(TOKEN_KEY, token, { expires: 7 }) // 7天过期
}

// 移除 Token
export function removeToken(): void {
  Cookies.remove(TOKEN_KEY)
}

// 检查是否已登录
export function isLoggedIn(): boolean {
  return !!getToken()
}