// 工作日志
export interface WorkLog {
  id: string
  employee_id: string
  log_date: string
  work_content: string
  completion_status: 'completed' | 'in_progress' | 'pending'
  problems_encountered: string
  tomorrow_plan: string
  self_rating: number
  supervisor_rating?: number
  supervisor_comment?: string
  created_at: string
  updated_at: string
  employee?: {
    id: string
    full_name: string
    username: string
  }
}

// 工作日志表单
export interface WorkLogForm {
  log_date: string
  work_content: string
  completion_status: 'completed' | 'in_progress' | 'pending'
  problems_encountered: string
  tomorrow_plan: string
  self_rating: number
  supervisor_rating?: number
  supervisor_comment?: string
}

// 工作日志搜索参数
export interface WorkLogSearchParams {
  employee_id?: string
  start_date?: string
  end_date?: string
  completion_status?: 'completed' | 'in_progress' | 'pending'
  page: number
  size: number
}

// 导出任务状态
export interface ExportTask {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  download_url?: string
  error_message?: string
  created_at: string
}