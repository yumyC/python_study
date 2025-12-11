import { defineStore } from 'pinia'
import { ref } from 'vue'
import { menuApi } from '@/api/menu'
import type { MenuItem } from '@/types/menu'

export const useMenuStore = defineStore('menu', () => {
  // 状态
  const menus = ref<MenuItem[]>([])
  const loading = ref(false)

  // 获取用户菜单
  const getUserMenus = async () => {
    loading.value = true
    try {
      const response = await menuApi.getUserMenus()
      menus.value = response.data
      return response.data
    } catch (error) {
      console.error('获取菜单失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 构建菜单树
  const buildMenuTree = (menuList: MenuItem[]): MenuItem[] => {
    const menuMap = new Map<string, MenuItem>()
    const rootMenus: MenuItem[] = []

    // 创建菜单映射
    menuList.forEach(menu => {
      menuMap.set(menu.id, { ...menu, children: [] })
    })

    // 构建树形结构
    menuList.forEach(menu => {
      const menuItem = menuMap.get(menu.id)!
      
      if (menu.parent_id) {
        const parent = menuMap.get(menu.parent_id)
        if (parent) {
          parent.children = parent.children || []
          parent.children.push(menuItem)
        }
      } else {
        rootMenus.push(menuItem)
      }
    })

    return rootMenus
  }

  // 获取菜单树
  const getMenuTree = async () => {
    const menuList = await getUserMenus()
    return buildMenuTree(menuList)
  }

  return {
    // 状态
    menus,
    loading,
    
    // 方法
    getUserMenus,
    buildMenuTree,
    getMenuTree
  }
})