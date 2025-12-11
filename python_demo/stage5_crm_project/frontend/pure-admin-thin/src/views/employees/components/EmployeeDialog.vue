<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEdit ? '编辑员工' : '添加员工'"
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
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              :disabled="isEdit"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="姓名" prop="full_name">
            <el-input
              v-model="form.full_name"
              placeholder="请输入姓名"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="邮箱" prop="email">
            <el-input
              v-model="form.email"
              placeholder="请输入邮箱"
              type="email"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="状态" prop="status">
            <el-select v-model="form.status" placeholder="请选择状态">
              <el-option label="激活" value="active" />
              <el-option label="禁用" value="inactive" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="岗位" prop="position_id">
            <el-select
              v-model="form.position_id"
              placeholder="请选择岗位"
              filterable
            >
              <el-option
                v-for="position in positions"
                :key="position.id"
                :label="position.name"
                :value="position.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="角色" prop="role_id">
            <el-select
              v-model="form.role_id"
              placeholder="请选择角色"
              filterable
            >
              <el-option
                v-for="role in roles"
                :key="role.id"
                :label="role.name"
                :value="role.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item v-if="!isEdit" label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          show-password
        />
      </el-form-item>
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
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { employeeApi } from '@/api/employee'
import type { Employee, EmployeeForm } from '@/types/employee'

// Props
interface Props {
  modelValue: boolean
  employee?: Employee | null
}

const props = withDefaults(defineProps<Props>(), {
  employee: null
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)
const positions = ref<any[]>([])
const roles = ref<any[]>([])

// 是否编辑模式
const isEdit = computed(() => !!props.employee)

// 表单数据
const form = reactive<EmployeeForm>({
  username: '',
  email: '',
  password: '',
  full_name: '',
  position_id: '',
  role_id: '',
  status: 'active'
})

// 表单验证规则
const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度在 6 到 100 个字符', trigger: 'blur' }
  ],
  position_id: [
    { required: true, message: '请选择岗位', trigger: 'change' }
  ],
  role_id: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 监听员工数据变化
watch(
  () => props.employee,
  (employee) => {
    if (employee) {
      Object.assign(form, {
        username: employee.username,
        email: employee.email,
        full_name: employee.full_name,
        position_id: employee.position_id,
        role_id: employee.role_id,
        status: employee.status,
        password: '' // 编辑时不显示密码
      })
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    username: '',
    email: '',
    password: '',
    full_name: '',
    position_id: '',
    role_id: '',
    status: 'active'
  })
  formRef.value?.clearValidate()
}

// 加载岗位列表
const loadPositions = async () => {
  try {
    // 这里应该调用岗位API
    // 暂时使用模拟数据
    positions.value = [
      { id: '1', name: '总经理', code: 'GM' },
      { id: '2', name: '技术总监', code: 'CTO' },
      { id: '3', name: '产品经理', code: 'PM' },
      { id: '4', name: '开发工程师', code: 'DEV' },
      { id: '5', name: '测试工程师', code: 'QA' }
    ]
  } catch (error) {
    console.error('加载岗位列表失败:', error)
  }
}

// 加载角色列表
const loadRoles = async () => {
  try {
    // 这里应该调用角色API
    // 暂时使用模拟数据
    roles.value = [
      { id: '1', name: '超级管理员', code: 'SUPER_ADMIN' },
      { id: '2', name: '管理员', code: 'ADMIN' },
      { id: '3', name: '普通用户', code: 'USER' }
    ]
  } catch (error) {
    console.error('加载角色列表失败:', error)
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    if (isEdit.value && props.employee) {
      // 编辑员工
      const updateData = { ...form }
      delete updateData.password // 编辑时不更新密码
      await employeeApi.updateEmployee(props.employee.id, updateData)
      ElMessage.success('更新员工成功')
    } else {
      // 添加员工
      await employeeApi.createEmployee(form)
      ElMessage.success('添加员工成功')
    }
    
    emit('success')
  } catch (error) {
    console.error('保存员工失败:', error)
    ElMessage.error('保存员工失败')
  } finally {
    loading.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  emit('update:modelValue', false)
  resetForm()
}

// 初始化
onMounted(() => {
  loadPositions()
  loadRoles()
})
</script>