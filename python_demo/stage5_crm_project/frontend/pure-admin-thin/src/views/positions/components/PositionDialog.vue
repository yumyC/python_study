<template>
  <el-dialog
    :model-value="modelValue"
    :title="getTitle()"
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
      <el-form-item v-if="parentPosition" label="上级岗位">
        <el-input :model-value="parentPosition.name" disabled />
      </el-form-item>
      
      <el-form-item label="岗位名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="请输入岗位名称"
        />
      </el-form-item>
      
      <el-form-item label="岗位编码" prop="code">
        <el-input
          v-model="form.code"
          placeholder="请输入岗位编码"
        />
      </el-form-item>
      
      <el-form-item label="岗位描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="请输入岗位描述"
        />
      </el-form-item>
      
      <el-form-item label="层级" prop="level">
        <el-input-number
          v-model="form.level"
          :min="1"
          :max="10"
          placeholder="岗位层级"
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

// 岗位接口类型
interface Position {
  id: string
  name: string
  code: string
  description: string
  level: number
  parent_id?: string
  created_at: string
  updated_at: string
}

// 岗位表单类型
interface PositionForm {
  name: string
  code: string
  description: string
  level: number
  parent_id?: string
}

// Props
interface Props {
  modelValue: boolean
  position?: Position | null
  parentPosition?: Position | null
}

const props = withDefaults(defineProps<Props>(), {
  position: null,
  parentPosition: null
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
const isEdit = computed(() => !!props.position)

// 表单数据
const form = reactive<PositionForm>({
  name: '',
  code: '',
  description: '',
  level: 1
})

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入岗位名称', trigger: 'blur' },
    { min: 2, max: 50, message: '岗位名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入岗位编码', trigger: 'blur' },
    { min: 2, max: 20, message: '岗位编码长度在 2 到 20 个字符', trigger: 'blur' },
    { pattern: /^[A-Z0-9_]+$/, message: '岗位编码只能包含大写字母、数字和下划线', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入岗位描述', trigger: 'blur' },
    { min: 5, max: 200, message: '岗位描述长度在 5 到 200 个字符', trigger: 'blur' }
  ],
  level: [
    { required: true, message: '请输入岗位层级', trigger: 'change' },
    { type: 'number', min: 1, max: 10, message: '岗位层级范围为 1-10', trigger: 'change' }
  ]
}

// 获取标题
const getTitle = () => {
  if (props.parentPosition) {
    return `添加下级岗位 - ${props.parentPosition.name}`
  }
  return isEdit.value ? '编辑岗位' : '添加岗位'
}

// 监听岗位数据变化
watch(
  () => [props.position, props.parentPosition],
  ([position, parentPosition]) => {
    if (position) {
      Object.assign(form, {
        name: position.name,
        code: position.code,
        description: position.description,
        level: position.level,
        parent_id: position.parent_id
      })
    } else {
      resetForm()
      if (parentPosition) {
        form.parent_id = parentPosition.id
        form.level = parentPosition.level + 1
      }
    }
  },
  { immediate: true }
)

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    name: '',
    code: '',
    description: '',
    level: 1,
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
    if (isEdit.value && props.position) {
      // 编辑岗位
      // await positionApi.updatePosition(props.position.id, form)
      ElMessage.success('更新岗位成功')
    } else {
      // 添加岗位
      // await positionApi.createPosition(form)
      ElMessage.success('添加岗位成功')
    }
    
    emit('success')
  } catch (error) {
    console.error('保存岗位失败:', error)
    ElMessage.error('保存岗位失败')
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