<template>
  <el-dialog
    :model-value="modelValue"
    :title="getTitle()"
    width="600px"
    @update:model-value="$emit('update:modelValue', $event)"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="formRules"
      label-width="100px"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item v-if="parentMenu" label="父菜单">
            <el-input :model-value="parentMenu.name" disabled />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="菜单名称" prop="name">
            <el-input
              v-model="form.name"
              placeholder="请输入菜单名称"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="路由路径" prop="path">
            <el-input
              v-model="form.path"
              placeholder="请输入路由路径"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="图标" prop="icon">
            <el-select
              v-model="form.icon"
              placeholder="请选择图标"
              filterable
              clearable
            >
              <el-option
                v-for="icon in iconOptions"
                :key="icon.value"
                :label="icon.label"
                :value="icon.value"
              >
                <div style="display: flex; align-items: center; gap: 8px;">
                  <el-icon><component :is="icon.value" /></el-icon>
                  <span>{{ icon.label }}</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="组件路径" prop="component">
            <el-input
              v-model="form.component"
              placeholder="请输入组件路径"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="排序" prop="sort_order">
            <el-input-number
              v-model="form.sort_order"
              :min="0"
              :max="999"
              placeholder="排序值"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="是否可见" prop="is_visible">
            <el-switch
              v-model="form.is_visible"
              active-text="可见"
              inactive-text="隐藏"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ loading ? '保存中...' : '保存' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { MenuItem, MenuForm } from '@/types/menu'

// Props
interface Props {
  modelValue: boolean
  menu?: MenuItem | null
  parentMenu?: MenuItem | null
}

const props = withDefaults(defineProps<Props>(), {
  menu: null,
  parentMenu: null
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)

// 是否编辑模式
const isEdit = computed(() => !!props.menu)

// 图标选项
const iconOptions = [
  { label: '仪表盘', value: 'Dashboard' },
  { label: '用户', value: 'User' },
  { label: '用户组', value: 'UserFilled' },
  { label: '公文包', value: 'Briefcase' },
  { label: '菜单', value: 'Menu' },
  { label: '锁', value: 'Lock' },
  { label: '文档', value: 'Document' },
  { label: '设置', value: 'Setting' },
  { label: '文件夹', value: 'Folder' },
  { label: '图表', value: 'DataAnalysis' }
]

// 表单数据
const form = reactive<MenuForm>({
  name: '',
  path: '',
  icon: '',
  component: '',
  sort_order: 0,
  is_visible: true
})

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入菜单名称', trigger: 'blur' },
    { min: 2, max: 50, message: '菜单名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  path: [
    { required: true, message: '请输入路由路径', trigger: 'blur' },
    { pattern: /^\/[a-zA-Z0-9\-_\/]*$/, message: '路由路径格式不正确', trigger: 'blur' }
  ],
  sort_order: [
    { required: true, message: '请输入排序值', trigger: 'change' },
    { type: 'number', min: 0, max: 999, message: '排序值范围为 0-999', trigger: 'change' }
  ]
}

// 获取标题
const getTitle = () => {
  if (props.parentMenu) {
    return `添加子菜单 - ${props.parentMenu.name}`
  }
  return isEdit.value ? '编辑菜单' : '添加菜单'
}

// 监听菜单数据变化
watch(
  () => [props.menu, props.parentMenu],
  ([menu, parentMenu]) => {
    if (menu) {
      Object.assign(form, {
        name: menu.name,
        path: menu.path,
        icon: menu.icon || '',
        component: menu.component || '',
        sort_order: menu.sort_order,
        is_visible: menu.is_visible,
        parent_id: menu.parent_id
      })
    } else {
      resetForm()
      if (parentMenu) {
        form.parent_id = parentMenu.id
      }
    }
  },
  { immediate: true }
)

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    name: '',
    path: '',
    icon: '',
    component: '',
    sort_order: 0,
    is_visible: true,
    parent_id: undefined
  })
  formRef.value?.clearValidate()
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    // 这里应该调用实际的API
    if (isEdit.value && props.menu) {
      // 编辑菜单
      // await menuApi.updateMenu(props.menu.id, form)
      ElMessage.success('更新菜单成功')
    } else {
      // 添加菜单
      // await menuApi.createMenu(form)
      ElMessage.success('添加菜单成功')
    }
    
    emit('success')
  } catch (error) {
    console.error('保存菜单失败:', error)
    ElMessage.error('保存菜单失败')
  } finally {
    loading.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  emit('update:modelValue', false)
  resetForm()
}
</script>