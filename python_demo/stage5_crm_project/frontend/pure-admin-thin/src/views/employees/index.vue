<template>
  <div class="page-container">
    <div class="page-header">
      <h2>员工管理</h2>
    </div>
    
    <!-- 搜索和操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchForm.search"
          placeholder="搜索员工姓名或用户名"
          style="width: 240px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.status"
          placeholder="员工状态"
          style="width: 120px"
          clearable
          @change="handleSearch"
        >
          <el-option label="激活" value="active" />
          <el-option label="禁用" value="inactive" />
        </el-select>
        
        <el-button type="primary" :icon="Search" @click="handleSearch">
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
      
      <div class="toolbar-right">
        <el-button type="primary" :icon="Plus" @click="handleAdd">
          添加员工
        </el-button>
        <el-button 
          type="danger" 
          :icon="Delete" 
          :disabled="selectedIds.length === 0"
          @click="handleBatchDelete"
        >
          批量删除
        </el-button>
      </div>
    </div>
    
    <!-- 员工表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="tableData"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="username" label="用户名" width="120" />
        
        <el-table-column prop="full_name" label="姓名" width="120" />
        
        <el-table-column prop="email" label="邮箱" width="200" />
        
        <el-table-column prop="position.name" label="岗位" width="120" />
        
        <el-table-column prop="role.name" label="角色" width="120" />
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at, 'YYYY-MM-DD HH:mm') }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="warning" size="small" @click="handleResetPassword(row)">
              重置密码
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
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
    
    <!-- 员工表单对话框 -->
    <EmployeeDialog
      v-model="dialogVisible"
      :employee="currentEmployee"
      @success="handleDialogSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Delete } from '@element-plus/icons-vue'
import { employeeApi } from '@/api/employee'
import type { Employee, EmployeeSearchParams } from '@/types/employee'
import { formatDate } from '@/utils/export'
import EmployeeDialog from './components/EmployeeDialog.vue'

// 响应式数据
const loading = ref(false)
const dialogVisible = ref(false)
const tableData = ref<Employee[]>([])
const selectedIds = ref<string[]>([])
const currentEmployee = ref<Employee | null>(null)

// 搜索表单
const searchForm = reactive({
  search: '',
  status: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 加载员工列表
const loadEmployees = async () => {
  loading.value = true
  try {
    const params: EmployeeSearchParams = {
      page: pagination.page,
      size: pagination.size,
      search: searchForm.search || undefined,
      status: searchForm.status as any || undefined
    }
    
    const response = await employeeApi.getEmployees(params)
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    console.error('加载员工列表失败:', error)
    ElMessage.error('加载员工列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadEmployees()
}

// 重置搜索
const handleReset = () => {
  searchForm.search = ''
  searchForm.status = ''
  pagination.page = 1
  loadEmployees()
}

// 添加员工
const handleAdd = () => {
  currentEmployee.value = null
  dialogVisible.value = true
}

// 编辑员工
const handleEdit = (employee: Employee) => {
  currentEmployee.value = employee
  dialogVisible.value = true
}

// 删除员工
const handleDelete = async (employee: Employee) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除员工 "${employee.full_name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await employeeApi.deleteEmployee(employee.id)
    ElMessage.success('删除成功')
    loadEmployees()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除员工失败:', error)
      ElMessage.error('删除员工失败')
    }
  }
}

// 批量删除
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 个员工吗？`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await employeeApi.batchDeleteEmployees(selectedIds.value)
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    loadEmployees()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

// 重置密码
const handleResetPassword = async (employee: Employee) => {
  try {
    const { value: newPassword } = await ElMessageBox.prompt(
      `请输入 "${employee.full_name}" 的新密码`,
      '重置密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /^.{6,}$/,
        inputErrorMessage: '密码长度至少6位'
      }
    )
    
    await employeeApi.resetPassword(employee.id, newPassword)
    ElMessage.success('密码重置成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重置密码失败:', error)
      ElMessage.error('重置密码失败')
    }
  }
}

// 表格选择变化
const handleSelectionChange = (selection: Employee[]) => {
  selectedIds.value = selection.map(item => item.id)
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadEmployees()
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadEmployees()
}

// 对话框成功回调
const handleDialogSuccess = () => {
  dialogVisible.value = false
  loadEmployees()
}

// 初始化
onMounted(() => {
  loadEmployees()
})
</script>

<style scoped>
.el-pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>