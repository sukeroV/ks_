<template>
  <div class="practice-detail">
    <el-card v-loading="loading" class="practice-card">
      <template #header>
        <div class="card-header">
          <h2>口算练习</h2>
          <div class="timer" :class="{ 'warning': remainingTime <= 30 }">
            剩余时间: {{ formatTime(remainingTime) }}
          </div>
        </div>
      </template>

      <div class="practice-content">
        <!-- 统计信息 -->
        <div v-if="isCompleted" class="statistics-bar">
          <div class="stat-item">
            <span>总题数：{{ totalQuestions }}</span>
          </div>
          <div class="stat-item">
            <span>正确题数：{{ correctAnswers }}</span>
          </div>
          <div class="stat-item">
            <span>正确率：{{ ((correctAnswers / totalQuestions) * 100).toFixed(1) }}%</span>
          </div>
          <div class="action-buttons">
            <el-button type="primary" size="small" @click="router.push('/history')">
              查看练习历史
            </el-button>
            <el-button size="small" @click="router.push('/practice')">
              继续练习
            </el-button>
          </div>
        </div>

        <!-- 题目列表 uuu-->
        <div class="expressions-list">
          <div 
            v-for="(expression, index) in expressions" 
            :key="index"
            class="expression-item"
          >
            <div class="expression-content">
              <span class="expression-number">{{ index + 1 }}.</span>
              <span class="expression-text">{{ expression.expression_text }} = </span>
              <el-input
                v-model="answers[index]"
                type="number"
                :placeholder="`请输入答案`"
                class="answer-input"
                :ref="el => answerInputs[index] = el"
                @focus="handleFocus(index)"
                @blur="handleBlur(index)"
                @keyup.enter="focusNext(index)"
                :disabled="isCompleted"
              />
              <span v-if="isCompleted" class="result-text" :class="{ 'wrong': !answerResults[index]?.is_correct, 'correct': answerResults[index]?.is_correct }">
                正确答案: {{ answerResults[index]?.correct_answer }}
              </span>
            </div>
          </div>
        </div>

        <!-- 提交按钮 -->
        <div class="submit-section" v-if="!isCompleted">
          <el-button 
            type="primary" 
            @click="submitAllAnswers"
            :loading="isSubmitting"
            size="large"
          >
            提交答案
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const isSubmitting = ref(false)
const remainingTime = ref<number>(0)
const timer = ref<number | null>(null)
const expressions = ref<any[]>([])
const answers = ref<string[]>([])
const answerInputs = ref<any[]>([])
const showResultDialog = ref(false)
const answerTimes = ref<{ [key: number]: number }>({})
const startTimes = ref<{ [key: number]: number }>({})
const pauseTimes = ref<{ [key: number]: number }>({})
const correctAnswers = ref(0)
const totalQuestions = ref(0)
const exerciseSet = ref<any>(null)
const isCompleted = ref(false)
const answerResults = ref<any[]>([])

// 格式化时间
const formatTime = (seconds: number) => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

// 添加本地存储相关的方法
const STORAGE_KEY = (id: string) => `practice_${id}_`

// 保存答题状态到本地存储
const saveProgress = () => {
  const practiceId = route.params.id as string
  const data = {
    answers: answers.value,
    remainingTime: remainingTime.value,
    startTimes: startTimes.value,
    pauseTimes: pauseTimes.value,
    answerTimes: answerTimes.value,
    isCompleted: isCompleted.value
  }
  
  // 使用一次性保存所有数据，避免多次写入
  localStorage.setItem(STORAGE_KEY(practiceId), JSON.stringify(data))
}

// 从本地存储恢复答题状态
const loadProgress = () => {
  const practiceId = route.params.id as string
  const savedData = localStorage.getItem(STORAGE_KEY(practiceId))
  
  if (savedData) {
    try {
      const data = JSON.parse(savedData)
      answers.value = data.answers || []
      remainingTime.value = parseInt(data.remainingTime) || 0
      startTimes.value = data.startTimes || {}
      pauseTimes.value = data.pauseTimes || {}
      answerTimes.value = data.answerTimes || {}
      isCompleted.value = data.isCompleted || false
    } catch (e) {
      console.error('加载保存的进度失败:', e)
    }
  }
}

// 清除本地存储的答题状态
const clearProgress = () => {
  const practiceId = route.params.id as string
  localStorage.removeItem(STORAGE_KEY(practiceId))
}

// 获取练习数据
const fetchExerciseData = async () => {
  try {
    loading.value = true
    const exerciseResponse = await axios.get(`/api/exercise-set/${route.params.id}`)
    exerciseSet.value = exerciseResponse.data
    
    const expressionsResponse = await axios.get(
      `/api/exercise-set/${route.params.id}/expressions`
    )
    expressions.value = expressionsResponse.data
    
    // 初始化答案数组
    if (!answers.value.length) {
      answers.value = new Array(expressions.value.length).fill('')
    }
    
    // 尝试加载已保存的进度
    loadProgress()
    
    // 只有在没有保存的时间的情况下才初始化时间
    if (remainingTime.value === 0 && exerciseSet.value.time_limit > 0) {
      remainingTime.value = exerciseSet.value.time_limit * 60
    }
    
    // 如果有剩余时间且未完成，启动计时器
    if (remainingTime.value > 0 && !isCompleted.value) {
      startTimer()
    }
  } catch (error) {
    console.error('获取练习数据失败:', error)
    ElMessage.error('获取练习数据失败')
    router.push('/practice')
  } finally {
    loading.value = false
  }
}

// 开始计时器
const startTimer = () => {
  // 清除可能存在的旧计时器
  if (timer.value) {
    clearInterval(timer.value)
  }
  
  timer.value = setInterval(() => {
    if (remainingTime.value <= 0) {
      clearInterval(timer.value)
      handleTimeUp()
      return
    }
    remainingTime.value--
    // 每次更新时间时保存进度
    saveProgress()
  }, 1000)
}

// 聚焦下一个输入框
const focusNext = (currentIndex: number) => {
  if (currentIndex < expressions.value.length - 1) {
    answerInputs.value[currentIndex + 1]?.focus()
  }
}

// 处理输入框获得焦点
const handleFocus = (index: number) => {
  const now = Date.now();
  if (!startTimes.value[index]) {
    // 第一次聚焦
    startTimes.value[index] = now;
  } else if (pauseTimes.value[index]) {
    // 重新聚焦，计算暂停时间
    const pauseDuration = now - pauseTimes.value[index];
    startTimes.value[index] = startTimes.value[index] + pauseDuration;
  }
  pauseTimes.value[index] = 0; // 清除暂停时间
}

// 处理输入框失去焦点
const handleBlur = (index: number) => {
  if (startTimes.value[index] && !pauseTimes.value[index]) {
    const now = Date.now();
    const timeSpent = (now - startTimes.value[index]) / 1000; // 转换为秒
    answerTimes.value[index] = (answerTimes.value[index] || 0) + timeSpent;
    pauseTimes.value[index] = now; // 记录暂停开始时间
  }
}

// 修改倒计时处理
const handleTimeUp = async () => {
  if (isCompleted.value) return // 如果已经完成了就不再处理
  
  ElMessage.warning('时间到，练习已自动提交！')
  // 调用提交答案方法，传入 true 表示是超时提交
  await submitAllAnswers(true)
}

// 修改提交答案的方法
const submitAllAnswers = async (isTimeout = false) => {
  if (isSubmitting.value) return
  
  try {
    isSubmitting.value = true
    
    // 立即停止计时器
    if (timer.value) {
      clearInterval(timer.value)
      timer.value = null
    }
    
    // 计算所有未完成计时的题目
    expressions.value.forEach((_, index) => {
      if (startTimes.value[index] && !pauseTimes.value[index]) {
        handleBlur(index)
      }
    })

    // 准备批量提交的数据
    const answersData = expressions.value.map((expr, index) => {
      const answerTime = Math.round(answerTimes.value[index] || 0)
      return {
        expression_id: expr.expression_id,
        user_answer: answers.value[index] || 0, // 如果没答题就默认为0
        answer_time: answerTime
      }
    })

    // 只在手动提交时检查未完成题目
    if (!isTimeout) {
      const unfinished = answersData.findIndex((data, index) => !answers.value[index])
      if (unfinished !== -1) {
        ElMessage.warning(`请完成第 ${unfinished + 1} 题`)
        answerInputs.value[unfinished]?.focus()
        isSubmitting.value = false
        // 如果有未完成的题目，重新启动计时器
        if (remainingTime.value > 0) {
          startTimer()
        }
        return
      }
    }

    // 批量提交答案
    const response = await axios.post('/api/answer-records/batch', {
      answers: answersData
    })

    // 更新答题结果
    const results = response.data.results
    let correctCount = 0
    answerResults.value = results  // 保存每道题的结果
    results.forEach((result: any) => {
      if (result.is_correct) {
        correctCount++
      }
    })

    // 完成练习
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const actualDuration = exerciseSet.value.time_limit * 60 - remainingTime.value
    
    await axios.post(`/api/exercise-set/${route.params.id}/complete`, {
      user_id: user.user_id,
      duration: actualDuration,
      is_timeout: isTimeout // 添加是否超时标记
    })

    // 更新状态
    isCompleted.value = true
    correctAnswers.value = correctCount
    totalQuestions.value = expressions.value.length
    remainingTime.value = 0

    // 显示结果统计
    ElMessage.success(`练习完成！正确率: ${((correctCount / expressions.value.length) * 100).toFixed(1)}%`)

    // 提交成功后清除本地存储
    clearProgress()
  } catch (error) {
    console.error('提交答案失败:', error)
    ElMessage.error('提交答案失败')
  } finally {
    isSubmitting.value = false
  }
}

// 添加自动保存功能
let autoSaveTimer: number | null = null

const startAutoSave = () => {
  autoSaveTimer = setInterval(() => {
    if (!isCompleted.value) {
      saveProgress()
    }
  }, 1000) // 每秒保存一次
}

// 在组件挂载时启动自动保存
onMounted(() => {
  fetchExerciseData()
  startAutoSave()
})

// 在组件卸载时清理
onBeforeUnmount(() => {
  if (timer.value) {
    clearInterval(timer.value)
  }
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
  }
  // 如果练习未完成，保存进度
  if (!isCompleted.value) {
    saveProgress()
  }
})

// 监听页面刷新和关闭
window.addEventListener('beforeunload', () => {
  if (!isCompleted.value) {
    saveProgress()
  }
})
</script>

<style scoped>
.practice-detail {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timer {
  font-size: 20px;
  font-weight: 500;
  color: #409EFF;
  padding: 6px 12px;
  border-radius: 4px;
  background-color: #ecf5ff;
}

.timer.warning {
  color: #E6A23C;
  background-color: #fdf6ec;
}

.expressions-list {
  padding: 20px;
  display: grid;
  gap: 15px;
}

.expression-item {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 12px 16px;
  transition: background-color 0.3s;
}

.expression-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.expression-number {
  font-weight: 500;
  color: #909399;
  min-width: 24px;
}

.expression-text {
  font-size: 16px;
  color: #303133;
  flex: 1;
  text-align: right;
  padding-right: 8px;
}

.answer-input {
  width: 100px;
}

.result-text {
  min-width: 120px;
  font-size: 14px;
}

.result-text.wrong {
  color: #f56c6c;
}

.result-text.correct {
  color: #67c23a;
}

.submit-section {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

:deep(.el-input__inner) {
  text-align: center;
  font-size: 16px;
  padding: 0 8px;
}

:deep(.el-input.is-disabled .el-input__inner) {
  color: #606266;
  -webkit-text-fill-color: #606266;
  background-color: #f5f7fa;
}

/* 添加一些响应式布局 */
@media (max-width: 768px) {
  .expression-content {
    flex-wrap: wrap;
  }
  
  .answer-input {
    width: 80px;
  }
  
  .result-text {
    width: 100%;
    margin-top: 8px;
    text-align: right;
  }
}

.result-content {
  padding: 20px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-size: 16px;
}

.dialog-footer {
  text-align: center;
}

.statistics-bar {
  background-color: #f0f9eb;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-item {
  font-size: 16px;
  color: #67c23a;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.result-indicator {
  display: flex;
  align-items: center;
  margin-left: 10px;
  gap: 8px;
}

.correct {
  color: #67c23a;
}

.wrong {
  color: #f56c6c;
}

.correct-answer {
  color: #f56c6c;
  font-size: 14px;
}

.timer-wrapper {
  position: fixed;
  top: 80px;
  right: 20px;
  padding: 8px 16px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 100;
}

.timer-wrapper.time-warning {
  background-color: #fef0f0;
  color: #f56c6c;
}

.remaining-time {
  font-size: 16px;
  font-weight: 500;
  font-family: monospace;
}
</style> 