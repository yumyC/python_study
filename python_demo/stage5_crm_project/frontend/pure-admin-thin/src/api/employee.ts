import { request } from '@/utils/request'
import type { Employee, EmployeeForm, EmployeeSearchParams } from '@/types/employee'
import type { PaginationResponse } from '@/types/common'

export const employeeApi = {
  // 获取员工列表
  getEmployees(params: EmployeeSearchParams) {
    return request.get<PaginationResponse<Employee>>('/employees', { params })
  },

  // 获取员工详情
  getEmployee(id: string) {
    return request.get<Employee>(`/employees/${id}`)
  },

  // 创建员工
  createEmployee(data: EmployeeForm) {
    return request.post<Employee>('/employees', data)
  },

  // 更新员工
  updateEmployee(id: string, data: Partial<EmployeeForm>) {
    return request.put<Employee>(`/employees/${id}`, data)
  },

  // 删除员工
  deleteEmployee(id: string) {
    return request.delete(`/employees/${id}`)
  },

  // 批量删除员工
  batchDeleteEmployees(ids: string[]) {
    return request.delete('/employees/batch', { data: { ids } })
  },

  // 重置员工密码
  resetPassword(id: string, newPassword: string) {
    return request.post(`/employees/${id}/reset-password`, { password: newPassword })
  }
}