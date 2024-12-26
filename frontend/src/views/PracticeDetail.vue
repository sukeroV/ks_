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
        <!-- 题目列表 -->
        <div class="expressions-list">
          <div 
            v-for="(expression, index) in expressions" 
            :key="index"
            class="expression-item"
          >
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
            />
          </div>
        </div>

        <!-- 提交按钮 -->
        <div class="submit-section">
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

    <!-- 完成对话框 -->
    <el-dialog
      v-model="showResultDialog"
      title="练习完成"
      width="400px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div class="result-content">
        <div class="result-item">
          <span>总题数：</span>
          <span>{{ totalQuestions }}</span>
        </div>
        <div class="result-item">
          <span>正确题数：</span>
          <span>{{ correctAnswers }}</span>
        </div>
        <div class="result-item">
          <span>正确率：</span>
          <span>{{ ((correctAnswers / totalQuestions) * 100).toFixed(1) }}%</span>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="router.push('/history')">
            查看练习历史
          </el-button>
          <el-button @click="router.push('/practice')">
            继续练习
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const isSubmitting = ref(false)
const remainingTime = ref(0)
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

// 格式化时间
const formatTime = (seconds: number) => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

// 获取练习数据
const fetchExerciseData = async () => {
  try {
    loading.value = true
    const exerciseResponse = await axios.get(`/api/exercise-set/${route.params.id}`)
    exerciseSet.value = exerciseResponse.data
    
    if (exerciseSet.value.time_limit > 0) {
      remainingTime.value = exerciseSet.value.time_limit * 60
      startTimer()
    }
    
    const expressionsResponse = await axios.get(
      `/api/exercise-set/${route.params.id}/expressions`
    )
    expressions.value = expressionsResponse.data
    answers.value = new Array(expressions.value.length).fill('')
    
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
  timer.value = window.setInterval(() => {
    if (remainingTime.value > 0) {
      remainingTime.value--
    } else {
      // 时间到了自动提交
      submitAllAnswers(false)  // 改为 false，不再标记为超时
    }
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

// 提交所有答案
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
        handleBlur(index);
      }
    });

    // 准备批量提交的数据
    const answersData = expressions.value.map((expr, index) => {
      const answerTime = Math.round(answerTimes.value[index] || 0); // 四舍五入到整数秒
      return {
        expression_id: expr.expression_id,
        user_answer: answers.value[index] || 0,
        answer_time: answerTime
      };
    });

    // 检查所有题目是否已完成（只在手动提交时检查）
    if (!isTimeout) {
      const unfinished = answersData.findIndex((data, index) => !answers.value[index]);
      if (unfinished !== -1) {
        ElMessage.warning(`请完成第 ${unfinished + 1} 题`);
        answerInputs.value[unfinished]?.focus();
        isSubmitting.value = false;
        // 如果有未完成的题目，重新启动计时器
        if (remainingTime.value > 0) {
          startTimer();
        }
        return;
      }
    }

    // 批量提交答案
    const response = await axios.post('/api/answer-records/batch', {
      answers: answersData
    });

    // 更新答题结果
    const results = response.data.results;
    let correctCount = 0;
    results.forEach((result: any) => {
      if (result.is_correct) {
        correctCount++;
      }
    });

    // 完成练习
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const actualDuration = exerciseSet.value.time_limit * 60 - remainingTime.value
    
    await axios.post(`/api/exercise-set/${route.params.id}/complete`, {
      user_id: user.user_id,
      duration: actualDuration,
      is_timeout: false  // 始终设置为 false，因为我们不再使用超时状态
    })

    // 显示结果对话框
    showResultDialog.value = true
    correctAnswers.value = correctCount
    totalQuestions.value = expressions.value.length
    remainingTime.value = 0 // 清空剩余时间显示
    
  } catch (error) {
    console.error('提交答案失败:', error)
    ElMessage.error('提交答案失败')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchExerciseData()
})

onUnmounted(() => {
  if (timer.value) {
    clearInterval(timer.value)
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
}

.expression-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.expression-number {
  font-weight: bold;
  margin-right: 10px;
  color: #909399;
  width: 30px;
}

.expression-text {
  font-size: 18px;
  margin-right: 10px;
  flex: 1;
}

.answer-input {
  width: 120px;
}

.submit-section {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

:deep(.el-input__inner) {
  text-align: center;
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
</style> 