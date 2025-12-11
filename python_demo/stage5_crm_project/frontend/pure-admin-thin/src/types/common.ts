// 通用响应结构
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页参数
export interface PaginationParams {
  page: number
  size: number
  search?: string
}

// 分页响应
export interface PaginationResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// 表格列配置
export interface TableColumn {
  prop: string
  label: string
  width?: number | string
  minWidth?: number | string
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  formatter?: (row: any, column: any, cellValue: any) => string
}

// 表单规则
export interface FormRule {
  required?: boolean
  message?: string
  trigger?: string | string[]
  min?: number
  max?: number
  pattern?: RegExp
  validator?: (rule: any, value: any, callback: any) => void
}

// 选项
export interface Option {
  label: string
  value: string | number
  disabled?: boolean
}

// 树形节点
export interface TreeNode {
  id: string
  label: string
  children?: TreeNode[]
  disabled?: boolean
  [key: string]: any
}