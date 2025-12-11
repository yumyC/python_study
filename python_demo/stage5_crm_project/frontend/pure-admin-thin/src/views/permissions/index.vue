<template>
  <div class="page-container">
    <div class="page-header">
      <h2>权限管理</h2>
    </div>
    
    <!-- 角色选择 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select
          v-model="selectedRoleId"
          placeholder="请选择角色"
          style="width: 200px"
          @change="handleRoleChange"
        >
          <el-option
            v-for="role in roles"
            :key="role.id"
            :label="role.name"
            :value="role.id"
          />
        </el-select>
        <el-button type="primary" :disabled="!selectedRoleId" @click="loadPermissions">
          查看权限
        </el-button>
      </div>
      
      <div class="toolbar-right">
        <el-button 
          type="success" 
          :disabled="!selectedRoleId"
          :loading="saveLoading"
          @click="handleSave"
        >
          保存权限
        </el-button>
      </div>
    </div>
    
    <!-- 权限配置 -->
    <div v-if="selectedRoleId" class="permission-container">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>{{ selectedRole?.name }} - 权限配置</span>
            <div class="header-actions">
              <el-button size="small" @click="expandAll">全部展开</el-button>
              <el-button size="small" @click="collapseAll">全部收起</el-button>
              <el-button size="small" type="primary" @click="checkAll">全选</el-button>
              <el-button size="small" @click="uncheckAll">取消全选</el-button>
            </div>
          </div>
        </template>
        
        <el-tree
          ref="permissionTreeRef"
          v-loading="loading"
          :data="menuTree"
          :props="treeProps"
          show-checkbox
          node-key="id"
          :default-checked-keys="checkedKeys"
          :default-expanded-keys="expandedKeys"
          @check="handleCheck"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <div class="node-info">
                <el-icon v-if="data.icon">
                  <component :is="data.icon" />
                </el-icon>
                <span class="node-label">{{ data.name }}</span>
                <el-tag v-if="data.path" size="small" type="info">{{ data.path }}</el-tag>
              </div>
              
              <div v-if="!data.children || data.children.length === 0" class="node-permissions">
                <el-checkbox-group
                  :model-value="getNodePermissions(data.id)"
                  @change="handlePermissionChange(data.id, $event)"
                >
                  <el-checkbox label="view">查看</el-checkbox>
                  <el-checkbox label="create">创建</el-checkbox>
                  <el-checkbox label="update">更新</el-checkbox>
                  <el-checkbox label="delete">删除</el-checkbox>
                </el-checkbox-group>
              </div>
            </div>
          </template>
        </el-tree>
      </el-card>
    </div>
    
    <div v-else class="empty-state">
      <el-empty description="请选择角色查看权限配置" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { ElTree } from 'element-plus'
import type { MenuItem } from '@/types/menu'

// 角色接口类型
interface Role {
  id: string
  name: string
  code: string
  description: string
}

// 权限接口类型
interface Permission {
  menu_id: string
  permissions: string[]
}

// 响应式数据
const loading = ref(false)
const saveLoading = ref(false)
const selectedRoleId = ref('')
const roles = ref<Role[]>([])
const menuTree = ref<MenuItem[]>([])
const checkedKeys = ref<string[]>([])
const expandedKeys = ref<string[]>([])
const permissionTreeRef = ref<InstanceType<typeof ElTree>>()

// 权限映射
const rolePermissions = reactive<Record<string, string[]>>({})

// 树形组件属性
const treeProps = {
  children: 'children',
  label: 'name'
}

// 当前选中的角色
const selectedRole = computed(() => {
  return roles.value.find(role => role.id === selectedRoleId.value)
})

// 模拟数据
const mockRoles: Role[] = [
  { id: '1', name: '超级管理员', code: 'SUPER_ADMIN', description: '系统超级管理员' },
  { id: '2', name: '管理员', code: 'ADMIN', description: '系统管理员' },
  { id: '3', name: '普通用户', code: 'USER', description: '普通用户' }
]

const mockMenuTree: MenuItem[] = [
  {
    id: '1',
    name: '系统管理',
    path: '/system',
    icon: 'Setting',
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
    sort_order: 2,
    is_visible: true,
    created_at: '2024-01-04T00:00:00Z',
    updated_at: '2024-01-04T00:00:00Z'
  }
]

// 加载角色列表
const loadRoles = async () => {
  try {
    // 这里应该调用实际的API
    // const response = await roleApi.getRoles()
    // roles.value = response.data
    
    // 暂时使用模拟数据
    roles.value = mockRoles
  } catch (error) {
    console.error('加载角色列表失败:', error)
    ElMessage.error('加载角色列表失败')
  }
}

// 加载菜单树
const loadMenuTree = async () => {
  try {
    // 这里应该调用实际的API
    // const response = await menuApi.getMenuTree()
    // menuTree.value = response.data
    
    // 暂时使用模拟数据
    menuTree.value = mockMenuTree
    
    // 默认展开所有节点
    expandedKeys.value = getAllNodeIds(menuTree.value)
  } catch (error) {
    console.error('加载菜单树失败:', error)
    ElMessage.error('加载菜单树失败')
  }
}

// 获取所有节点ID
const getAllNodeIds = (nodes: MenuItem[]): string[] => {
  const ids: string[] = []
  
  const traverse = (nodeList: MenuItem[]) => {
    nodeList.forEach(node => {
      ids.push(node.id)
      if (node.children && node.children.length > 0) {
        traverse(node.children)
      }
    })
  }
  
  traverse(nodes)
  return ids
}

// 角色变化处理
const handleRoleChange = () => {
  checkedKeys.value = []
  Object.keys(rolePermissions).forEach(key => {
    delete rolePermissions[key]
  })
}

// 加载权限配置
const loadPermissions = async () => {
  if (!selectedRoleId.value) return
  
  loading.value = true
  try {
    // 这里应该调用实际的API
    // const response = await permissionApi.getRolePermissions(selectedRoleId.value)
    // const permissions = response.data
    
    // 暂时使用模拟数据
    const permissions: Permission[] = [
      { menu_id: '2', permissions: ['view', 'create', 'update'] },
      { menu_id: '4', permissions: ['view', 'create'] }
    ]
    
    // 重置权限映射
    Object.keys(rolePermissions).forEach(key => {
      delete rolePermissions[key]
    })
    
    // 设置权限映射
    permissions.forEach(permission => {
      rolePermissions[permission.menu_id] = permission.permissions
    })
    
    // 设置选中的菜单节点
    checkedKeys.value = permissions.map(p => p.menu_id)
  } catch (error) {
    console.error('加载权限配置失败:', error)
    ElMessage.error('加载权限配置失败')
  } finally {
    loading.value = false
  }
}

// 获取节点权限
const getNodePermissions = (nodeId: string): string[] => {
  return rolePermissions[nodeId] || []
}

// 权限变化处理
const handlePermissionChange = (nodeId: string, permissions: string[]) => {
  rolePermissions[nodeId] = permissions
}

// 树节点选中处理
const handleCheck = (data: MenuItem, checked: any) => {
  if (checked.checkedKeys.includes(data.id)) {
    // 节点被选中，设置默认权限
    if (!rolePermissions[data.id]) {
      rolePermissions[data.id] = ['view']
    }
  } else {
    // 节点被取消选中，清除权限
    delete rolePermissions[data.id]
  }
}

// 全部展开
const expandAll = () => {
  expandedKeys.value = getAllNodeIds(menuTree.value)
}

// 全部收起
const collapseAll = () => {
  expandedKeys.value = []
}

// 全选
const checkAll = () => {
  const allIds = getAllNodeIds(menuTree.value)
  checkedKeys.value = allIds
  
  // 设置所有节点的默认权限
  allIds.forEach(id => {
    if (!rolePermissions[id]) {
      rolePermissions[id] = ['view']
    }
  })
}

// 取消全选
const uncheckAll = () => {
  checkedKeys.value = []
  Object.keys(rolePermissions).forEach(key => {
    delete rolePermissions[key]
  })
}

// 保存权限
const handleSave = async () => {
  if (!selectedRoleId.value) return
  
  saveLoading.value = true
  try {
    // 构建权限数据
    const permissions: Permission[] = Object.entries(rolePermissions).map(([menuId, perms]) => ({
      menu_id: menuId,
      permissions: perms
    }))
    
    // 这里应该调用实际的API
    // await permissionApi.updateRolePermissions(selectedRoleId.value, permissions)
    
    ElMessage.success('保存权限成功')
  } catch (error) {
    console.error('保存权限失败:', error)
    ElMessage.error('保存权限失败')
  } finally {
    saveLoading.value = false
  }
}

// 初始化
onMounted(() => {
  loadRoles()
  loadMenuTree()
})
</script>

<style scoped>
.permission-container {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 20px;
}

.node-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-label {
  font-weight: 500;
}

.node-permissions {
  display: flex;
  gap: 8px;
}

.empty-state {
  margin-top: 100px;
}

:deep(.el-tree-node__content) {
  height: auto;
  padding: 8px 0;
}

:deep(.el-checkbox-group) {
  display: flex;
  gap: 12px;
}

:deep(.el-checkbox) {
  margin-right: 0;
}
</style>