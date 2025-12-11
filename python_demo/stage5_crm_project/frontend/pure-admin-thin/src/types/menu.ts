// 菜单项
export interface MenuItem {
  id: string
  name: string
  path: string
  icon?: string
  component?: string
  parent_id?: string
  sort_order: number
  is_visible: boolean
  created_at: string
  updated_at: string
  children?: MenuItem[]
  permissions?: string[]
}

// 菜单表单
export interface MenuForm {
  name: string
  path: string
  icon?: string
  component?: string
  parent_id?: string
  sort_order: number
  is_visible: boolean
}

// 权限类型
export type PermissionType = 'view' | 'create' | 'update' | 'delete'