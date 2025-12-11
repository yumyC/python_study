import { request } from '@/utils/request'
import type { WorkLog, WorkLogForm, WorkLogSearchParams, ExportTask } from '@/types/worklog'
import type { PaginationResponse } from '@/types/common'

export const workLogApi = {
  // 获取工作日志列表
  getWorkLogs(params: WorkLogSearchParams) {
    return request.get<PaginationResponse<WorkLog>>('/work-logs', { params })
  },

  // 获取工作日志详情
  getWorkLog(id: string) {
    return request.get<WorkLog>(`/work-logs/${id}`)
  },

  // 创建工作日志
  createWorkLog(data: WorkLogForm) {
    return request.post<WorkLog>('/work-logs', data)
  },

  // 更新工作日志
  updateWorkLog(id: string, data: Partial<WorkLogForm>) {
    return request.put<WorkLog>(`/work-logs/${id}`, data)
  },

  // 删除工作日志
  deleteWorkLog(id: string) {
    return request.delete(`/work-logs/${id}`)
  },

  // 上级评分
  rateWorkLog(id: string, rating: number, comment?: string) {
    return request.post(`/work-logs/${id}/rate`, { 
      supervisor_rating: rating, 
      supervisor_comment: comment 
    })
  },

  // 导出工作日志
  exportWorkLogs(params: Omit<WorkLogSearchParams, 'page' | 'size'>) {
    return request.post<{ task_id: string }>('/work-logs/export', params)
  },

  // 获取导出任务状态
  getExportTaskStatus(taskId: string) {
    return request.get<ExportTask>(`/tasks/${taskId}/status`)
  },

  // 下载导出文件
  downloadExportFile(taskId: string) {
    return request.get(`/tasks/${taskId}/download`, { 
      responseType: 'blob' 
    })
  }
}