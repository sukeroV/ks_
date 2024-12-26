<template>
  <div class="practice-container">
    <div class="practice-layout">
      <!-- 左侧练习配置 -->
      <el-card class="config-card">
        <template #header>
          <div class="card-header">
            <h3>练习配置</h3>
          </div>
        </template>
        
        <el-form 
          :model="practiceForm" 
          :rules="rules" 
          ref="practiceFormRef"
          label-position="top"
          class="config-form"
        >
          <!-- 题目数量 -->
          <el-form-item label="题目数量" prop="total_expressions">
            <div class="number-input-wrapper">
              <el-button 
                @click="decreaseNumber('total_expressions', 5, 5, 100)"
                :disabled="practiceForm.total_expressions <= 5"
              >
                <el-icon><Minus /></el-icon>
              </el-button>
              <span class="number-display">{{ practiceForm.total_expressions }}</span>
              <el-button 
                @click="increaseNumber('total_expressions', 5, 5, 100)"
                :disabled="practiceForm.total_expressions >= 100"
              >
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </el-form-item>

          <!-- 56年级显示括号题目数量选择 -->
          <el-form-item 
            v-if="userGrade >= 5" 
            label="括号题目数量" 
            prop="bracket_expressions"
          >
            <div class="number-input-wrapper">
              <el-button 
                @click="decreaseNumber('bracket_expressions', 1, 1, getMaxBracketCount)"
                :disabled="practiceForm.bracket_expressions <= 1"
              >
                <el-icon><Minus /></el-icon>
              </el-button>
              <span class="number-display">{{ practiceForm.bracket_expressions }}</span>
              <el-button 
                @click="increaseNumber('bracket_expressions', 1, 1, getMaxBracketCount)"
                :disabled="practiceForm.bracket_expressions >= getMaxBracketCount"
              >
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </el-form-item>
          
          <!-- 时间限制 -->
          <el-form-item label="时间限制（分钟）" prop="time_limit">
            <div class="number-input-wrapper">
              <el-button 
                @click="decreaseNumber('time_limit', 1, 1, 60)"
                :disabled="practiceForm.time_limit <= 1"
              >
                <el-icon><Minus /></el-icon>
              </el-button>
              <span class="number-display">{{ practiceForm.time_limit }}</span>
              <el-button 
                @click="increaseNumber('time_limit', 1, 1, 60)"
                :disabled="practiceForm.time_limit >= 60"
              >
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="startPractice" style="width: 100%">
              开始练习
            </el-button>
          </el-form-item>

          <!-- 添加导入导出按钮 -->
          <div class="import-export-buttons">
            <el-button plain @click="importExpressions">
              <el-icon><Upload /></el-icon>
              导入题目
            </el-button>
            <el-button plain @click="exportExpressions">
              <el-icon><Download /></el-icon>
              导出题目
            </el-button>
          </div>
        </el-form>
      </el-card>

      <!-- 右侧练习说明 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <h3>练习说明</h3>
          </div>
        </template>
        
        <div class="info-content">
          <el-alert
            :title="`当前年级：${userGrade}年级`"
            type="info"
            :closable="false"
            show-icon
          >
            <template #default>
              <div class="grade-tip">
                系统会根据您的年级自动生成相应难度的题目
                <el-link 
                  type="primary" 
                  @click="router.push('/profile')"
                  class="grade-edit-link"
                >
                  修改年级 <el-icon><ArrowRight /></el-icon>
                </el-link>
              </div>
            </template>
          </el-alert>

          <h4>年级对应说明</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="一、二年级">
              <div class="difficulty-detail">
                - 只含加减法的算式
                - 数值范围：1-100
                - 每道题只有一个运算符
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="三、四年级">
              <div class="difficulty-detail">
                - 包含加减乘的算式
                - 数值范围：1-100
                - 每道题只有一个运算符
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="五、六年级">
              <div class="difficulty-detail">
                - 包含加减乘除的算式
                - 数值范围：1-100
                - 最多两个运算符
                - 包含括号题目
              </div>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>
    </div>

    <!-- 添加导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入题目"
      width="400px"
    >
      <el-upload
        class="upload-demo"
        :action="'/api/expressions/import'"
        :headers="uploadHeaders"
        :data="uploadData"
        :show-file-list="false"
        :on-success="handleImportSuccess"
        :on-error="handleImportError"
        accept=".csv"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            请上传包含"序号、算式、答案"三列的CSV文件
          </div>
        </template>
      </el-upload>
    </el-dialog>

    <!-- 添加导出对话框 -->
    <el-dialog
      v-model="exportDialogVisible"
      title="导出题目"
      width="400px"
    >
      <div class="export-options">
        <el-button @click="handleExport('docx')" type="primary" plain>
          <el-icon><Document /></el-icon>
          导出为 Word
        </el-button>
        <el-button @click="handleExport('csv')" type="primary" plain>
          <el-icon><Document /></el-icon>
          导出为 CSV
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Minus, ArrowRight, Upload, Download, Document, UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const practiceFormRef = ref()

// 获取用户年级
const userGrade = computed(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    const user = JSON.parse(userStr)
    return user.grade
  }
  return 1
})

// 根据年级获取最大括号题目数量
const getMaxBracketCount = computed(() => {
  return Math.min(9, practiceForm.value.total_expressions)
})

// 表单数据
const practiceForm = ref({
  total_expressions: 10,
  bracket_expressions: 1,
  time_limit: 3,
  operators: [] as string[],
  operator_count: 1,
  min_number: 1,
  max_number: 100
})

// 根据年级设置运算符和运算符数量
const setupPracticeConfig = () => {
  const grade = userGrade.value
  
  if (grade <= 2) {
    practiceForm.value.operators = ['+', '-']
    practiceForm.value.operator_count = 1
    practiceForm.value.bracket_expressions = 0
  } else if (grade <= 4) {
    practiceForm.value.operators = ['+', '-', '×']
    practiceForm.value.operator_count = 1
    practiceForm.value.bracket_expressions = 0
  } else {
    practiceForm.value.operators = ['+', '-', '×', '÷']
    practiceForm.value.operator_count = 2
    practiceForm.value.bracket_expressions = Math.min(practiceForm.value.bracket_expressions, 9)
  }
}

// 增加数值的方法
const increaseNumber = (field: string, step: number, min: number, max: number) => {
  const newValue = practiceForm.value[field] + step
  if (newValue <= max) {
    practiceForm.value[field] = newValue
  }
}

// 减少数值的方法
const decreaseNumber = (field: string, step: number, min: number, max: number) => {
  const newValue = practiceForm.value[field] - step
  if (newValue >= min) {
    practiceForm.value[field] = newValue
  }
}

// 开始练习
const startPractice = async () => {
  try {
    setupPracticeConfig()
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    
    const response = await axios.post('/api/exercise-set', {
      user_id: user.user_id,
      total_expressions: practiceForm.value.total_expressions,
      bracket_expressions: practiceForm.value.bracket_expressions,
      time_limit: practiceForm.value.time_limit,
      operators: practiceForm.value.operators,
      operator_count: practiceForm.value.operator_count,
      min_number: practiceForm.value.min_number,
      max_number: practiceForm.value.max_number
    })
    
    router.push(`/practice/${response.data.exercise_set_id}`)
  } catch (error) {
    console.error('创建练习失败:', error)
    ElMessage.error('创建练习失败')
  }
}

// 添加导入导出相关的响应式变量
const importDialogVisible = ref(false)
const exportDialogVisible = ref(false)

// 打开导入对话框
const importExpressions = () => {
  importDialogVisible.value = true
}

// 打开导出对话框
const exportExpressions = () => {
  exportDialogVisible.value = true
}

// 添加上传所需的数据
const uploadData = computed(() => ({
  user_id: JSON.parse(localStorage.getItem('user') || '{}').user_id
}))

// 添加上传所需的请求头
const uploadHeaders = {
  'Accept': 'application/json'
}

// 处理导入成功
const handleImportSuccess = (response) => {
  ElMessage.success('导入成功')
  importDialogVisible.value = false
  if (response.exercise_set_id) {
    router.push(`/practice/${response.exercise_set_id}`)
  }
}

// 处理导入失败
const handleImportError = (error) => {
  console.error('导入失败:', error)
  ElMessage.error(error.response?.data?.error || '导入失败')
}

// 处理导出
const handleExport = async (format: string) => {
  try {
    // 先设置练习配置
    setupPracticeConfig()
    
    const response = await axios.post('/api/expressions/export', {
      format,
      config: {
        total_expressions: practiceForm.value.total_expressions,
        bracket_expressions: practiceForm.value.bracket_expressions,
        operators: practiceForm.value.operators,
        operator_count: practiceForm.value.operator_count,
        min_number: practiceForm.value.min_number,
        max_number: practiceForm.value.max_number
      }
    }, {
      responseType: 'blob'
    })
    
    const blob = new Blob([response.data], {
      type: format === 'docx' 
        ? 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        : 'text/csv;charset=utf-8'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `口算练习_${new Date().toISOString().split('T')[0]}.${format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    exportDialogVisible.value = false
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}
</script>
<!-- 998 -->
<style scoped>
.practice-container {
  height: calc(100vh - 60px); /* 减去顶部导航栏的高度 */
  padding: 24px;
  box-sizing: border-box;
  background-color: #f5f7fa;
  overflow: hidden; /* 防止出现双滚动条 */
}

/* 左右布局样式优化 */
.practice-layout {
  display: flex;
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
  height: 100%; /* 使用父容器的全部高度 */
}

/* 左侧配置卡片 */
.config-card {
  flex: 0 0 380px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  height: 100%; /* 使用父容器的全部高度 */
}

/* 右侧说明卡片 */
.info-card {
  flex: 1;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  height: 100%; /* 使用父容器的全部高度 */
}

/* 卡片标题 */
.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fff;
  flex-shrink: 0; /* 防止标题被压缩 */
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

/* 配置表单和说明内容 */
.config-form,
.info-content {
  padding: 20px;
  flex: 1; /* 占据剩余空间 */
  overflow-y: auto; /* 内容过多时可滚动 */
}

/* 说明内容容器 */
.info-content {
  overflow-y: visible; /* 移除滚动条 */
}

/* 数字输入框组样式 */
.number-input-wrapper {
  display: flex;
  align-items: center;
  height: 36px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #fff;
}

.number-input-wrapper .el-button {
  width: 36px;
  height: 100%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
}

.number-display {
  flex: 1;
  text-align: center;
  font-size: 15px;
  color: #606266;
  user-select: none;
  line-height: 36px;
}

/* 开始练习按钮 */
:deep(.el-button--primary) {
  width: 100%;
  height: 40px;
  font-size: 15px;
  font-weight: 500;
}

/* 导入导出按钮组 */
.import-export-buttons {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px dashed #ebeef5;
}

.import-export-buttons .el-button {
  flex: 1;
  max-width: 120px;
}

.grade-tip {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #606266;
}

:deep(.el-descriptions) {
  margin-top: 16px;
}

:deep(.el-descriptions__cell) {
  padding: 16px 20px;
}

.difficulty-detail {
  color: #606266;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-line;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .practice-container {
    height: auto;
    overflow: visible;
  }

  .practice-layout {
    flex-direction: column;
    height: auto;
  }
  
  .config-card,
  .info-card {
    height: auto;
  }
  
  .config-form,
  .info-content {
    height: auto;
    overflow: visible;
  }
}
</style> 

<!--  -->

<!--  -->