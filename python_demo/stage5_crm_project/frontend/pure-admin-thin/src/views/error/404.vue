<template>
  <div class="error-page">
    <div class="error-content">
      <div class="error-image">
        <img src="/404.svg" alt="404" />
      </div>
      
      <div class="error-info">
        <h1>404</h1>
        <h2>页面不存在</h2>
        <p>抱歉，您访问的页面不存在或已被删除。</p>
        
        <div class="error-actions">
          <el-button type="primary" @click="goHome">
            返回首页
          </el-button>
          <el-button @click="goBack">
            返回上页
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

// 返回首页
const goHome = () => {
  router.push('/')
}

// 返回上一页
const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.error-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.error-content {
  display: flex;
  align-items: center;
  gap: 60px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  max-width: 800px;
}

.error-image {
  flex-shrink: 0;
}

.error-image img {
  width: 300px;
  height: auto;
}

.error-info {
  text-align: center;
}

.error-info h1 {
  font-size: 72px;
  font-weight: 700;
  color: #667eea;
  margin: 0 0 16px 0;
  line-height: 1;
}

.error-info h2 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
}

.error-info p {
  font-size: 16px;
  color: #606266;
  margin: 0 0 32px 0;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-content {
    flex-direction: column;
    gap: 32px;
    padding: 24px;
    margin: 20px;
  }
  
  .error-image img {
    width: 200px;
  }
  
  .error-info h1 {
    font-size: 48px;
  }
  
  .error-actions {
    flex-direction: column;
  }
}
</style>