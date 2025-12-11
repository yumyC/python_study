<template>
  <div class="page-container">
    <div class="page-header">
      <h2>菜单管理</h2>
    </div>
    
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Plus" @click="handleAdd">
          添加菜单
        </el-button>
        <el-button :icon="Refresh" @click="loadMenus">
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- 菜单表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="tableData"
        row-key="id"
        default-expand-all
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      >
        <el-table-column prop="name" label="菜单名称" width="200" />
        
        <el-table-column prop="path" label="路由路径" width="200" />
        
        <el-table-column prop="icon" label="图标" width="100">
          <template #default="{ row }">
            <el-icon v-if="row.icon">
              <component :is="row.icon" />
            </el-icon>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="component" label="组件" width="200" />
        
        <el-table-column prop="sort_order" label="排序" width="80" />
        
        <el-table-column prop="is_visible" label="可见" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_visible ? 'success' : 'danger'">
              {{ row.is_visible ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="success" size="small" @click="handleAddChild(row)">
              添加子菜单
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 菜单表单对话框 -->
    <MenuDialog
      v-model="dialogVisible"
      :menu="currentMenu"
      :parent-menu="parentMenu"
      @success="handleDialogSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import type { MenuItem } from '@/types/menu'
import MenuDialog from './components/MenuDialog.vue'

// 响应式数据
const loading = ref(false)
const dialogVisible = ref(false)
const tableData = ref<MenuItem[]>([])
const currentMenu = ref<MenuItem | null>(null)
const parentMenu = ref<MenuItem | null>(null)

// 模拟菜单数据
const mockMenus: MenuItem[] = [
  {
    id: '1',
    name: '系统管理',
    path: '/system',
    icon: 'Setting',
    component: '',
    sort_order: 1,
    is_visible: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    children: [
      {
        id: '2',
        name: '员工管理',
        path: '/employees',
        icon: 'User',
        component: 'employees/index',
        parent_id: '1',
        sort_order: 1,
        is_visible: true,
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z'
      },
      {
        id: '3',
        name: '角色管理',
        path: '/roles',
        icon: 'UserFilled',
        component: 'roles/index',
        parent_id: '1',
        sort_order: 2,
        is_visible: true,
        created_at: '2024-01-03T00:00:00Z',
        updated_at: '2024-01-03T00:00:00Z'
      }
    ]
  },
  {
    id: '4',
    name: '工作日志',
    path: '/work-logs',
    icon: 'Document',
    component: 'work-logs/index',
    sort_order: 2,
    is_visible: true,
    created_at: '2024-01-04T00:00:00Z',
    updated_at: '2024-01-04T00:00:00Z'
  }
]

// 加载菜单列表
const loadMenus = async () => {
  loading.value = true
  try {
    // 这里应该调用实际的API
    // const response = await menuApi.getMenus()
    // tableData.value = response.data
    
    // 暂时使用模拟数据
    await new Promise(resolve => setTimeout(resolve, 500))
    tableData.value = mockMenus
  } catch (error) {
    console.error('加载菜单列表失败:', error)
    ElMessage.error('加载菜单列表失败')
  } finally {
    loading.value = false
  }
}

// 添加菜单
const handleAdd = () => {
  currentMenu.value = null
  parentMenu.value = null
  dialogVisible.value = true
}

// 添加子菜单
const handleAddChild = (menu: MenuItem) => {
  currentMenu.value = null
  parentMenu.value = menu
  dialogVisible.value = true
}

// 编辑菜单
const handleEdit = (menu: MenuItem) => {
  currentMenu.value = menu
  parentMenu.value = null
  dialogVisible.value = true
}

// 删除菜单
const handleDelete = async (menu: MenuItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除菜单 "${menu.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里应该调用删除API
    // await menuApi.deleteMenu(menu.id)
    
    ElMessage.success('删除成功')
    loadMenus()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除菜单失败:', error)
      ElMessage.error('删除菜单失败')
    }
  }
}

// 对话框成功回调
const handleDialogSuccess = () => {
  dialogVisible.value = false
  loadMenus()
}

// 初始化
onMounted(() => {
  loadMenus()
})
</script>