<template>
  <div class="page-container">
    <div class="page-header">
      <h2>工作日志</h2>
    </div>
    
    <!-- 搜索和操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="handleSearch"
        />
        
        <el-select
          v-model="searchForm.completion_status"
          placeholder="完成状态"
          style="width: 120px"
          clearable
          @change="handleSearch"
        >
          <el-option label="已完成" value="completed" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="待开始" value="pending" />
        </el-select>
        
        <el-button type="primary" :icon="Search" @click="handleSearch">
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
      
      <div class="toolbar-right">
        <el-button type="primary" :icon="Plus" @click="handleAdd">
          写日志
        </el-button>
        <el-button 
          type="success" 
          :icon="Download" 
          :loading="exportLoading"
          @click="handleExport"
        >
          导出Excel
        </el-button>
      </div>
    </div>
    
    <!-- 工作日志表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="tableData"
        row-key="id"
      >
        <el-table-column prop="log_date" label="日期" width="120" />
        
        <el-table-column prop="employee.full_name" label="员工" width="100" />
        
        <el-table-column prop="work_content" label="工作内容" min-width="200">
          <template #default="{ row }">
            <div class="content-cell">
              {{ row.work_content }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="completion_status" label="完成状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.completion_status)">
              {{ getStatusText(row.completion_status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="self_rating" label="自评" width="80">
          <template #default="{ row }">
            <el-rate
              v-model="row.self_rating"
              disabled
              show-score
              text-color="#ff9900"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="supervisor_rating" label="上级评分" width="100">
          <template #default="{ row }">
            <el-rate
              v-if="row.supervisor_rating"
              v-model="row.supervisor_rating"
              disabled
              show-score
              text-color="#ff9900"
            />
            <span v-else class="text-muted">未评分</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button 
              v-if="canEdit(row)"
              type="warning" 
              size="small" 
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button 
              v-if="canRate(row)"
              type="success" 
              size="small" 
              @click="handleRate(row)"
            >
              评分
            </el-button>
            <el-button 
              v-if="canDelete(row)"
              type="danger" 
              size="small" 
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 工作日志表单对话框 -->
    <WorkLogDialog
      v-model="dialogVisible"
      :work-log="currentWorkLog"
      :mode="dialogMode"
      @success="handleDialogSuccess"
    />
    
    <!-- 评分对话框 -->
    <RatingDialog
      v-model="ratingDialogVisible"
      :work-log="currentWorkLog"
      @success="handleRatingSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Download } from '@element-plus/icons-vue'
import { workLogApi } from '@/api/worklog'
import { useAuthStore } from '@/stores/auth'
import type { WorkLog, WorkLogSearchParams } from '@/types/worklog'
import { formatDate, exportToExcel } from '@/utils/export'
import WorkLogDialog from './components/WorkLogDialog.vue'
import RatingDialog from './components/RatingDialog.vue'

const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const exportLoading = ref(false)
const dialogVisible = ref(false)
const ratingDialogVisible = ref(false)
const tableData = ref<WorkLog[]>([])
const currentWorkLog = ref<WorkLog | null>(null)
const dialogMode = ref<'view' | 'add' | 'edit'>('add')

// 日期范围
const dateRange = ref<[string, string] | null>(null)

// 搜索表单
const searchForm = reactive({
  completion_status: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 当前用户信息
const userInfo = computed(() => authStore.userInfo)

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap = {
    completed: 'success',
    in_progress: 'warning',
    pending: 'info'
  }
  return typeMap[status as keyof typeof typeMap] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap = {
    completed: '已完成',
    in_progress: '进行中',
    pending: '待开始'
  }
  return textMap[status as keyof typeof textMap] || status
}

// 是否可以编辑
const canEdit = (workLog: WorkLog) => {
  return workLog.employee_id === userInfo.value?.id
}

// 是否可以评分
const canRate = (workLog: WorkLog) => {
  // 这里应该根据实际的权限逻辑判断
  // 暂时简单判断：不是自己的日志就可以评分
  return workLog.employee_id !== userInfo.value?.id
}

// 是否可以删除
const canDelete = (workLog: WorkLog) => {
  return workLog.employee_id === userInfo.value?.id
}

// 加载工作日志列表
const loadWorkLogs = async () => {
  loading.value = true
  try {
    const params: WorkLogSearchParams = {
      page: pagination.page,
      size: pagination.size,
      completion_status: searchForm.completion_status as any || undefined
    }
    
    if (dateRange.value) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const response = await workLogApi.getWorkLogs(params)
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    console.error('加载工作日志失败:', error)
    ElMessage.error('加载工作日志失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadWorkLogs()
}

// 重置搜索
const handleReset = () => {
  dateRange.value = null
  searchForm.completion_status = ''
  pagination.page = 1
  loadWorkLogs()
}

// 查看日志
const handleView = (workLog: WorkLog) => {
  currentWorkLog.value = workLog
  dialogMode.value = 'view'
  dialogVisible.value = true
}

// 添加日志
const handleAdd = () => {
  currentWorkLog.value = null
  dialogMode.value = 'add'
  dialogVisible.value = true
}

// 编辑日志
const handleEdit = (workLog: WorkLog) => {
  currentWorkLog.value = workLog
  dialogMode.value = 'edit'
  dialogVisible.value = true
}

// 删除日志
const handleDelete = async (workLog: WorkLog) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${workLog.log_date} 的工作日志吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await workLogApi.deleteWorkLog(workLog.id)
    ElMessage.success('删除成功')
    loadWorkLogs()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除工作日志失败:', error)
      ElMessage.error('删除工作日志失败')
    }
  }
}

// 评分
const handleRate = (workLog: WorkLog) => {
  currentWorkLog.value = workLog
  ratingDialogVisible.value = true
}

// 导出Excel
const handleExport = async () => {
  exportLoading.value = true
  try {
    const params = {
      completion_status: searchForm.completion_status as any || undefined
    }
    
    if (dateRange.value) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    // 启动导出任务
    const response = await workLogApi.exportWorkLogs(params)
    const taskId = response.data.task_id
    
    ElMessage.success('导出任务已启动，请稍候...')
    
    // 轮询任务状态
    const checkStatus = async () => {
      try {
        const statusResponse = await workLogApi.getExportTaskStatus(taskId)
        const task = statusResponse.data
        
        if (task.status === 'completed' && task.download_url) {
          // 下载文件
          const downloadResponse = await workLogApi.downloadExportFile(taskId)
          const blob = new Blob([downloadResponse.data])
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `工作日志_${formatDate(new Date(), 'YYYY-MM-DD')}.xlsx`
          link.click()
          window.URL.revokeObjectURL(url)
          
          ElMessage.success('导出成功')
        } else if (task.status === 'failed') {
          ElMessage.error('导出失败：' + task.error_message)
        } else {
          // 继续轮询
          setTimeout(checkStatus, 2000)
        }
      } catch (error) {
        console.error('检查导出状态失败:', error)
        ElMessage.error('检查导出状态失败')
      }
    }
    
    setTimeout(checkStatus, 2000)
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exportLoading.value = false
  }
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadWorkLogs()
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadWorkLogs()
}

// 对话框成功回调
const handleDialogSuccess = () => {
  dialogVisible.value = false
  loadWorkLogs()
}

// 评分成功回调
const handleRatingSuccess = () => {
  ratingDialogVisible.value = false
  loadWorkLogs()
}

// 初始化
onMounted(() => {
  loadWorkLogs()
})
</script>

<style scoped>
.content-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.text-muted {
  color: #909399;
  font-size: 12px;
}

.el-pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>