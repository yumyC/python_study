<template>
  <el-dialog
    :model-value="modelValue"
    title="上级评分"
    width="500px"
    @update:model-value="$emit('update:modelValue', $event)"
    @close="handleClose"
  >
    <div v-if="workLog" class="rating-content">
      <div class="work-info">
        <h4>{{ workLog.employee?.full_name }} - {{ workLog.log_date }}</h4>
        <div class="work-summary">
          <p><strong>工作内容：</strong>{{ workLog.work_content }}</p>
          <p><strong>完成状态：</strong>{{ getStatusText(workLog.completion_status) }}</p>
          <p><strong>自评分数：</strong>{{ workLog.self_rating }} 分</p>
        </div>
      </div>
      
      <el-divider />
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="评分" prop="supervisor_rating">
          <el-rate
            v-model="form.supervisor_rating"
            show-score
            text-color="#ff9900"
            score-template="{value} 分"
          />
          <div class="rating-tips">
            <p>评分标准：</p>
            <p>5分 - 优秀，超额完成任务</p>
            <p>4分 - 良好，完成任务质量高</p>
            <p>3分 - 合格，按时完成任务</p>
            <p>2分 - 一般，基本完成任务</p>
            <p>1分 - 较差，未能完成任务</p>
          </div>
        </el-form-item>
        
        <el-form-item label="评语" prop="supervisor_comment">
          <el-input
            v-model="form.supervisor_comment"
            type="textarea"
            :rows="4"
            placeholder="请输入评语和建议"
          />
        </el-form-item>
      </el-form>
    </div>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ loading ? '提交中...' : '提交评分' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { workLogApi } from '@/api/worklog'
import type { WorkLog } from '@/types/worklog'

// Props
interface Props {
  modelValue: boolean
  workLog?: WorkLog | null
}

const props = withDefaults(defineProps<Props>(), {
  workLog: null
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
const form = reactive({
  supervisor_rating: 3,
  supervisor_comment: ''
})

// 表单验证规则
const formRules: FormRules = {
  supervisor_rating: [
    { required: true, message: '请进行评分', trigger: 'change' },
    { type: 'number', min: 1, max: 5, message: '评分范围为1-5分', trigger: 'change' }
  ],
  supervisor_comment: [
    { required: true, message: '请输入评语', trigger: 'blur' },
    { min: 5, message: '评语至少5个字符', trigger: 'blur' }
  ]
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap = {
    completed: '已完成',
    in_progress: '进行中',
    pending: '待开始'
  }
  return textMap[status as keyof typeof textMap] || status
}

// 监听工作日志数据变化
watch(
  () => props.workLog,
  (workLog) => {
    if (workLog) {
      form.supervisor_rating = workLog.supervisor_rating || 3
      form.supervisor_comment = workLog.supervisor_comment || ''
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

// 重置表单
const resetForm = () => {
  form.supervisor_rating = 3
  form.supervisor_comment = ''
  formRef.value?.clearValidate()
}

// 提交评分
const handleSubmit = async () => {
  if (!formRef.value || !props.workLog) return
  
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    await workLogApi.rateWorkLog(
      props.workLog.id,
      form.supervisor_rating,
      form.supervisor_comment
    )
    
    ElMessage.success('评分提交成功')
    emit('success')
  } catch (error) {
    console.error('提交评分失败:', error)
    ElMessage.error('提交评分失败')
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

<style scoped>
.rating-content {
  padding: 0 8px;
}

.work-info h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
}

.work-summary p {
  margin: 8px 0;
  color: #606266;
  line-height: 1.5;
}

.rating-tips {
  margin-top: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  color: #909399;
}

.rating-tips p {
  margin: 4px 0;
  line-height: 1.4;
}

.rating-tips p:first-child {
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
}
</style>