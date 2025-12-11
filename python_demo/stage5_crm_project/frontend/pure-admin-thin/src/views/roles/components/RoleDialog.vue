<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEdit ? '编辑角色' : '添加角色'"
    width="500px"
    @update:model-value="$emit('update:modelValue', $event)"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="formRules"
      label-width="100px"
    >
      <el-form-item label="角色名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="请输入角色名称"
        />
      </el-form-item>
      
      <el-form-item label="角色编码" prop="code">
        <el-input
          v-model="form.code"
          placeholder="请输入角色编码"
          :disabled="isEdit"
        />
      </el-form-item>
      
      <el-form-item label="角色描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="4"
          placeholder="请输入角色描述"
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
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

// 角色接口类型
interface Role {
  id: string
  name: string
  code: string
  description: string
  created_at: string
  updated_at: string
}

// 角色表单类型
interface RoleForm {
  name: string
  code: string
  description: string
}

// Props
interface Props {
  modelValue: boolean
  role?: Role | null
}

const props = withDefaults(defineProps<Props>(), {
  role: null
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
const isEdit = computed(() => !!props.role)

// 表单数据
const form = reactive<RoleForm>({
  name: '',
  code: '',
  description: ''
})

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '角色名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { min: 2, max: 50, message: '角色编码长度在 2 到 50 个字符', trigger: 'blur' },
    { pattern: /^[A-Z0-9_]+$/, message: '角色编码只能包含大写字母、数字和下划线', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入角色描述', trigger: 'blur' },
    { min: 5, max: 200, message: '角色描述长度在 5 到 200 个字符', trigger: 'blur' }
  ]
}

// 监听角色数据变化
watch(
  () => props.role,
  (role) => {
    if (role) {
      Object.assign(form, {
        name: role.name,
        code: role.code,
        description: role.description
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
    name: '',
    code: '',
    description: ''
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
    if (isEdit.value && props.role) {
      // 编辑角色
      // await roleApi.updateRole(props.role.id, form)
      ElMessage.success('更新角色成功')
    } else {
      // 添加角色
      // await roleApi.createRole(form)
      ElMessage.success('添加角色成功')
    }
    
    emit('success')
  } catch (error) {
    console.error('保存角色失败:', error)
    ElMessage.error('保存角色失败')
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