<template>
  <el-dialog
    :model-value="modelValue"
    :title="getTitle()"
    width="800px"
    @update:model-value="$emit('update:modelValue', $event)"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="formRules"
      :disabled="mode === 'view'"
      label-width="120px"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="日期" prop="log_date">
            <el-date-picker
              v-model="form.log_date"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="完成状态" prop="completion_status">
            <el-select v-model="form.completion_status" placeholder="请选择完成状态">
              <el-option label="已完成" value="completed" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="待开始" value="pending" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item label="工作内容" prop="work_content">
        <el-input
          v-model="form.work_content"
          type="textarea"
          :rows="4"
          placeholder="请详细描述今日的工作内容"
        />
      </el-form-item>
      
      <el-form-item label="遇到的问题" prop="problems_encountered">
        <el-input
          v-model="form.problems_encountered"
          type="textarea"
          :rows="3"
          placeholder="描述工作中遇到的问题和困难"
        />
      </el-form-item>
      
      <el-form-item label="明日计划" prop="tomorrow_plan">
        <el-input
          v-model="form.tomorrow_plan"
          type="textarea"
          :rows="3"
          placeholder="描述明日的工作计划和安排"
        />
      </el-form-item>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="自评分数" prop="self_rating">
            <el-rate
              v-model="form.self_rating"
              show-score
              text-color="#ff9900"
              score-template="{value} 分"
            />
          </el-form-item>
        </el-col>
        
        <el-col v-if="mode === 'view' && workLog?.supervisor_rating" :span="12">
          <el-form-item label="上级评分">
            <el-rate
              :model-value="workLog.supervisor_rating"
              disabled
              show-score
              text-color="#ff9900"
              score-template="{value} 分"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item v-if="mode === 'view' && workLog?.supervisor_comment" label="上级评语">
        <el-input
          :model-value="workLog.supervisor_comment"
          type="textarea"
          :rows="2"
          readonly
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">
        {{ mode === 'view' ? '关闭' : '取消' }}
      </el-button>
      <el-button 
        v-if="mode !== 'view'"
        type="primary" 
        :loading="loading" 
        @click="handleSubmit"
      >
        {{ loading ? '保存中...' : '保存' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { workLogApi } from '@/api/worklog'
import type { WorkLog, WorkLogForm } from '@/types/worklog'

// Props
interface Props {
  modelValue: boolean
  workLog?: WorkLog | null
  mode: 'view' | 'add' | 'edit'
}

const props = withDefaults(defineProps<Props>(), {
  workLog: null,
  mode: 'add'
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)

// 表单数据
const form = reactive<WorkLogForm>({
  log_date: '',
  work_content: '',
  completion_status: 'in_progress',
  problems_encountered: '',
  tomorrow_plan: '',
  self_rating: 3
})

// 表单验证规则
const formRules: FormRules = {
  log_date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ],
  work_content: [
    { required: true, message: '请输入工作内容', trigger: 'blur' },
    { min: 10, message: '工作内容至少10个字符', trigger: 'blur' }
  ],
  completion_status: [
    { required: true, message: '请选择完成状态', trigger: 'change' }
  ],
  problems_encountered: [
    { required: true, message: '请输入遇到的问题', trigger: 'blur' }
  ],
  tomorrow_plan: [
    { required: true, message: '请输入明日计划', trigger: 'blur' }
  ],
  self_rating: [
    { required: true, message: '请进行自评', trigger: 'change' },
    { type: 'number', min: 1, max: 5, message: '评分范围为1-5分', trigger: 'change' }
  ]
}

// 获取标题
const getTitle = () => {
  const titleMap = {
    view: '查看工作日志',
    add: '添加工作日志',
    edit: '编辑工作日志'
  }
  return titleMap[props.mode]
}

// 监听工作日志数据变化
watch(
  () => props.workLog,
  (workLog) => {
    if (workLog) {
      Object.assign(form, {
        log_date: workLog.log_date,
        work_content: workLog.work_content,
        completion_status: workLog.completion_status,
        problems_encountered: workLog.problems_encountered,
        tomorrow_plan: workLog.tomorrow_plan,
        self_rating: workLog.self_rating,
        supervisor_rating: workLog.supervisor_rating,
        supervisor_comment: workLog.supervisor_comment
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
    log_date: new Date().toISOString().split('T')[0], // 默认今天
    work_content: '',
    completion_status: 'in_progress',
    problems_encountered: '',
    tomorrow_plan: '',
    self_rating: 3
  })
  formRef.value?.clearValidate()
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    if (props.mode === 'edit' && props.workLog) {
      // 编辑工作日志
      await workLogApi.updateWorkLog(props.workLog.id, form)
      ElMessage.success('更新工作日志成功')
    } else {
      // 添加工作日志
      await workLogApi.createWorkLog(form)
      ElMessage.success('添加工作日志成功')
    }
    
    emit('success')
  } catch (error) {
    console.error('保存工作日志失败:', error)
    ElMessage.error('保存工作日志失败')
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