<template>
  <div class="page-container">
    <div class="page-header">
      <h2>岗位管理</h2>
    </div>
    
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索岗位名称或编码"
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
          添加岗位
        </el-button>
      </div>
    </div>
    
    <!-- 岗位表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="tableData"
        row-key="id"
        default-expand-all
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      >
        <el-table-column prop="name" label="岗位名称" width="200" />
        
        <el-table-column prop="code" label="岗位编码" width="150" />
        
        <el-table-column prop="description" label="岗位描述" min-width="200" />
        
        <el-table-column prop="level" label="层级" width="80" />
        
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
            <el-button type="success" size="small" @click="handleAddChild(row)">
              添加下级
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 岗位表单对话框 -->
    <PositionDialog
      v-model="dialogVisible"
      :position="currentPosition"
      :parent-position="parentPosition"
      @success="handleDialogSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { formatDate } from '@/utils/export'
import PositionDialog from './components/PositionDialog.vue'

// 岗位接口类型定义
interface Position {
  id: string
  name: string
  code: string
  description: string
  level: number
  parent_id?: string
  created_at: string
  updated_at: string
  children?: Position[]
}

// 响应式数据
const loading = ref(false)
const dialogVisible = ref(false)
const tableData = ref<Position[]>([])
const currentPosition = ref<Position | null>(null)
const parentPosition = ref<Position | null>(null)
const searchKeyword = ref('')

// 模拟岗位数据
const mockPositions: Position[] = [
  {
    id: '1',
    name: '总经理',
    code: 'GM',
    description: '公司最高管理者',
    level: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    children: [
      {
        id: '2',
        name: '技术总监',
        code: 'CTO',
        description: '技术部门负责人',
        level: 2,
        parent_id: '1',
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
        children: [
          {
            id: '4',
            name: '开发工程师',
            code: 'DEV',
            description: '软件开发工程师',
            level: 3,
            parent_id: '2',
            created_at: '2024-01-04T00:00:00Z',
            updated_at: '2024-01-04T00:00:00Z'
          },
          {
            id: '5',
            name: '测试工程师',
            code: 'QA',
            description: '软件测试工程师',
            level: 3,
            parent_id: '2',
            created_at: '2024-01-05T00:00:00Z',
            updated_at: '2024-01-05T00:00:00Z'
          }
        ]
      },
      {
        id: '3',
        name: '产品经理',
        code: 'PM',
        description: '产品规划和管理',
        level: 2,
        parent_id: '1',
        created_at: '2024-01-03T00:00:00Z',
        updated_at: '2024-01-03T00:00:00Z'
      }
    ]
  }
]

// 加载岗位列表
const loadPositions = async () => {
  loading.value = true
  try {
    // 这里应该调用实际的API
    // const response = await positionApi.getPositions()
    // tableData.value = response.data
    
    // 暂时使用模拟数据
    await new Promise(resolve => setTimeout(resolve, 500))
    tableData.value = mockPositions
  } catch (error) {
    console.error('加载岗位列表失败:', error)
    ElMessage.error('加载岗位列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  // 这里应该实现搜索逻辑
  ElMessage.info('搜索功能开发中...')
}

// 重置搜索
const handleReset = () => {
  searchKeyword.value = ''
  loadPositions()
}

// 添加岗位
const handleAdd = () => {
  currentPosition.value = null
  parentPosition.value = null
  dialogVisible.value = true
}

// 添加下级岗位
const handleAddChild = (position: Position) => {
  currentPosition.value = null
  parentPosition.value = position
  dialogVisible.value = true
}

// 编辑岗位
const handleEdit = (position: Position) => {
  currentPosition.value = position
  parentPosition.value = null
  dialogVisible.value = true
}

// 删除岗位
const handleDelete = async (position: Position) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除岗位 "${position.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里应该调用删除API
    // await positionApi.deletePosition(position.id)
    
    ElMessage.success('删除成功')
    loadPositions()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除岗位失败:', error)
      ElMessage.error('删除岗位失败')
    }
  }
}

// 对话框成功回调
const handleDialogSuccess = () => {
  dialogVisible.value = false
  loadPositions()
}

// 初始化
onMounted(() => {
  loadPositions()
})
</script>