<template>
  <div class="practice-container">
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

        <!-- 5�����6年级显示括号题目数量选择 -->
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

    <!-- 练习说明 -->
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
  time_limit: 10,
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

<style scoped>
.practice-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.grade-alert {
  margin-bottom: 20px;
}

.grade-info {
  margin-bottom: 24px;
}

.grade-tip {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.difficulty-detail {
  margin-top: 8px;
  color: #606266;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-line;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.config-card, .info-card {
  height: 100%;
}

.info-content {
  padding: 0 20px;
}

.info-content h4 {
  margin: 24px 0 16px;
  color: #303133;
  font-size: 16px;
}

.info-content h4:first-child {
  margin-top: 0;
}

:deep(.el-descriptions__label) {
  width: 100px;
  font-weight: bold;
}

:deep(.el-tag) {
  margin-right: 8px;
}

:deep(.el-alert) {
  margin-bottom: 12px;
}

:deep(.el-alert__title) {
  font-size: 14px;
}

:deep(.el-alert--info) {
  background-color: #f4f4f5;
  color: #606266;
}

:deep(.el-radio-group) {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-input-number .el-input__wrapper) {
  width: 100%;
}

.number-input-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 40px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.number-input-wrapper .el-button {
  height: 100%;
  margin: 0;
  padding: 0 15px;
  border: none;
  border-radius: 0;
  flex: 0 0 auto;
}

.number-display {
  flex: 1;
  text-align: center;
  font-size: 16px;
  color: #606266;
  user-select: none;
}

/* 悬停效果 */
.number-input-wrapper .el-button:not(:disabled):hover {
  background-color: #f5f7fa;
}

/* 禁用状态 */
.number-input-wrapper .el-button[disabled] {
  background-color: #f5f7fa;
  border-color: #dcdfe6;
}

.import-export-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
}

.export-options {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

:deep(.el-upload) {
  width: 100%;
}

.el-upload__tip {
  text-align: center;
  margin-top: 8px;
  color: #909399;
}
</style> 

<!--  -->

<!--  -->