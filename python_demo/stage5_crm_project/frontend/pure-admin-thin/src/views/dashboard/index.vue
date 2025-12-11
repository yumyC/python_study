<template>
  <div class="page-container">
    <div class="page-header">
      <h2>仪表盘</h2>
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon employee">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.employeeCount }}</div>
            <div class="stat-label">员工总数</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon position">
            <el-icon><Briefcase /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.positionCount }}</div>
            <div class="stat-label">岗位数量</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon role">
            <el-icon><UserFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.roleCount }}</div>
            <div class="stat-label">角色数量</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon worklog">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ stats.workLogCount }}</div>
            <div class="stat-label">今日日志</div>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 快速操作 -->
    <el-row :gutter="20" class="quick-actions">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>
          <div class="action-grid">
            <el-button 
              type="primary" 
              :icon="Plus" 
              @click="$router.push('/employees')"
            >
              添加员工
            </el-button>
            <el-button 
              type="success" 
              :icon="Document" 
              @click="$router.push('/work-logs')"
            >
              写日志
            </el-button>
            <el-button 
              type="warning" 
              :icon="Setting" 
              @click="$router.push('/roles')"
            >
              角色管理
            </el-button>
            <el-button 
              type="info" 
              :icon="Menu" 
              @click="$router.push('/menus')"
            >
              菜单管理
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>系统信息</span>
          </template>
          <div class="system-info">
            <div class="info-item">
              <span class="info-label">当前用户：</span>
              <span class="info-value">{{ userInfo?.full_name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">用户角色：</span>
              <span class="info-value">{{ userInfo?.role?.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">所属岗位：</span>
              <span class="info-value">{{ userInfo?.position?.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">登录时间：</span>
              <span class="info-value">{{ formatDate(new Date()) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { 
  User, 
  Briefcase, 
  UserFilled, 
  Document, 
  Plus, 
  Setting, 
  Menu 
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { formatDate } from '@/utils/export'

const authStore = useAuthStore()

// 用户信息
const userInfo = computed(() => authStore.userInfo)

// 统计数据
const stats = ref({
  employeeCount: 0,
  positionCount: 0,
  roleCount: 0,
  workLogCount: 0
})

// 加载统计数据
const loadStats = async () => {
  try {
    // 这里应该调用实际的统计接口
    // 暂时使用模拟数据
    stats.value = {
      employeeCount: 25,
      positionCount: 8,
      roleCount: 5,
      workLogCount: 12
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
}

.stat-icon.employee {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.position {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.role {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.worklog {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.quick-actions {
  margin-bottom: 24px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.action-grid .el-button {
  justify-self: stretch;
}

.system-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  color: #909399;
  font-size: 14px;
}

.info-value {
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
}
</style>