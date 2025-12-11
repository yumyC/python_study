<template>
  <div class="page-container">
    <div class="page-header">
      <h2>角色管理</h2>
    </div>
    
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索角色名称或编码"
          style="width: 240px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" :icon="Search" @click="handleSearch">
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
      
      <div class="toolbar-right">
        <el-button type="primary" :icon="Plus" @click="handleAdd">
          添加角色
        </el-button>
      </div>
    </div>
    
    <!-- 角色表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="tableData"
      >
        <el-table-column prop="name" label="角色名称" width="150" />
        
        <el-table-column prop="code" label="角色编码" width="150" />
        
        <el-table-column prop="description" label="角色描述" min-width="200" />
        
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
            <el-button type="success" size="small" @click="handlePermissions(row)">
              权限配置
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
    
    <!-- 角色表单对话框 -->
    <RoleDialog
      v-model="dialogVisible"
      :role="currentRole"
      @success="handleDialogSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { formatDate } from '@/utils/export'
import RoleDialog from './components/RoleDialog.vue'

// 角色接口类型
interface Role {
  id: string
  name: string
  code: string
  description: string
  created_at: string
  updated_at: string
}

// 响应式数据
const loading = ref(false)
const dialogVisible = ref(false)
const tableData = ref<Role[]>([])
const currentRole = ref<Role | null>(null)
const searchKeyword = ref('')

// 分页信息
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 模拟角色数据
const mockRoles: Role[] = [
  {
    id: '1',
    name: '超级管理员',
    code: 'SUPER_ADMIN',
    description: '系统超级管理员，拥有所有权限',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  },
  {
    id: '2',
    name: '管理员',
    code: 'ADMIN',
    description: '系统管理员，拥有大部分管理权限',
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z'
  },
  {
    id: '3',
    name: '普通用户',
    code: 'USER',
    description: '普通用户，拥有基本操作权限',
    created_at: '2024-01-03T00:00:00Z',
    updated_at: '2024-01-03T00:00:00Z'
  }
]

// 加载角色列表
const loadRoles = async () => {
  loading.value = true
  try {
    // 这里应该调用实际的API
    // const response = await roleApi.getRoles(params)
    // tableData.value = response.data.items
    // pagination.total = response.data.total
    
    // 暂时使用模拟数据
    await new Promise(resolve => setTimeout(resolve, 500))
    tableData.value = mockRoles
    pagination.total = mockRoles.length
  } catch (error) {
    console.error('加载角色列表失败:', error)
    ElMessage.error('加载角色列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadRoles()
}

// 重置搜索
const handleReset = () => {
  searchKeyword.value = ''
  pagination.page = 1
  loadRoles()
}

// 添加角色
const handleAdd = () => {
  currentRole.value = null
  dialogVisible.value = true
}

// 编辑角色
const handleEdit = (role: Role) => {
  currentRole.value = role
  dialogVisible.value = true
}

// 权限配置
const handlePermissions = (role: Role) => {
  ElMessage.info(`配置角色 "${role.name}" 的权限功能开发中...`)
}

// 删除角色
const handleDelete = async (role: Role) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色 "${role.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里应该调用删除API
    // await roleApi.deleteRole(role.id)
    
    ElMessage.success('删除成功')
    loadRoles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除角色失败:', error)
      ElMessage.error('删除角色失败')
    }
  }
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadRoles()
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadRoles()
}

// 对话框成功回调
const handleDialogSuccess = () => {
  dialogVisible.value = false
  loadRoles()
}

// 初始化
onMounted(() => {
  loadRoles()
})
</script>

<style scoped>
.el-pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>