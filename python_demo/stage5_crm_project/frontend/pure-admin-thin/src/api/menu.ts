import { request } from '@/utils/request'
import type { MenuItem, MenuForm } from '@/types/menu'

export const menuApi = {
  // 获取菜单列表
  getMenus() {
    return request.get<MenuItem[]>('/menus')
  },

  // 获取用户菜单
  getUserMenus() {
    return request.get<MenuItem[]>('/menus/user')
  },

  // 获取菜单详情
  getMenu(id: string) {
    return request.get<MenuItem>(`/menus/${id}`)
  },

  // 创建菜单
  createMenu(data: MenuForm) {
    return request.post<MenuItem>('/menus', data)
  },

  // 更新菜单
  updateMenu(id: string, data: Partial<MenuForm>) {
    return request.put<MenuItem>(`/menus/${id}`, data)
  },

  // 删除菜单
  deleteMenu(id: string) {
    return request.delete(`/menus/${id}`)
  },

  // 获取菜单树
  getMenuTree() {
    return request.get<MenuItem[]>('/menus/tree')
  }
}