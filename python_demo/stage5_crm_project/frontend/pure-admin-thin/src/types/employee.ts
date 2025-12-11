// 员工信息
export interface Employee {
  id: string
  username: string
  email: string
  full_name: string
  position_id: string
  role_id: string
  status: 'active' | 'inactive'
  created_at: string
  updated_at: string
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
}

// 员工表单
export interface EmployeeForm {
  username: string
  email: string
  password?: string
  full_name: string
  position_id: string
  role_id: string
  status: 'active' | 'inactive'
}

// 员工搜索参数
export interface EmployeeSearchParams {
  search?: string
  position_id?: string
  role_id?: string
  status?: 'active' | 'inactive'
  page: number
  size: number
}