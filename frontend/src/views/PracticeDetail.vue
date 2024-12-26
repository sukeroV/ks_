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
        <!-- 进度条 -->
        <div class="progress-section">
          <el-progress 
            :percentage="(currentIndex + 1) / totalQuestions * 100" 
            :format="format"
            :stroke-width="12"
            class="progress-bar"
          />
        </div>

        <!-- 题目显示 -->
        <div class="expression-container" @click="focusInput">
          <div class="expression" v-if="currentExpression">
            {{ currentExpression }}
          </div>
          <div v-else class="loading-text">
            加载题目中...
          </div>
        </div>

        <!-- 答题区域 -->
        <div class="answer-section">
          <el-form 
            ref="answerFormRef"
            :model="answerForm"
            :rules="answerRules"
            @submit.prevent="submitAnswer"
          >
            <el-form-item prop="answer">
              <el-input
                ref="answerInput"
                v-model="answerForm.answer"
                :class="{ 'is-correct': currentStatus === 'success', 'is-wrong': currentStatus === 'error' }"
                placeholder="请输入答案"
                size="large"
                @keyup.enter="submitAnswer"
                :disabled="isSubmitting"
                autofocus
              >
                <template #append>
                  <el-button 
                    type="primary" 
                    @click="submitAnswer"
                    :loading="isSubmitting"
                    size="large"
                  >
                    提交
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-card>

    <!-- 添加答题完成对话框 -->
    <el-dialog
      v-model="showResultDialog"
      title="答题完成"
      width="80%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div v-loading="detailLoading">
        <!-- 统计信息 -->
        <div class="statistics-section">
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-card">
                <div class="stat-value">{{ totalQuestions }}</div>
                <div class="stat-label">总题数</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-card correct">
                <div class="stat-value">{{ correctCount }}</div>
                <div class="stat-label">正确题数</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-card">
                <div class="stat-value">{{ accuracy }}%</div>
                <div class="stat-label">正确率</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 答题详情表格 -->
        <div class="expressions-list">
          <h3>答题详情</h3>
          <el-table :data="answerDetails" border style="width: 100%">
            <el-table-column label="题目" prop="expression_text" />
            <el-table-column label="正确答案" width="120">
              <template #default="{ row }">
                {{ Number(row.answer).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="你的答案" width="120">
              <template #default="{ row }">
                {{ row.user_answer === '-' ? '-' : Number(row.user_answer).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="用时" width="100">
              <template #default="{ row }">
                {{ formatTime(row.answer_time) }}秒
              </template>
            </el-table-column>
            <el-table-column label="是否正确" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_correct ? 'success' : 'danger'">
                  {{ row.is_correct ? '正确' : '错误' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 底部按钮 -->
        <div class="dialog-footer">
          <el-button type="primary" @click="goToHistory">查看历史记录</el-button>
          <el-button @click="startNewPractice">继续练习</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

export default defineComponent({
  name: 'PracticeDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const answerFormRef = ref()
    const answerInput = ref()
    
    const loading = ref(true)
    const currentIndex = ref(0)
    const totalQuestions = ref(0)
    const expressions = ref<any[]>([])
    const currentExpression = ref('')
    const remainingTime = ref(0)
    const isSubmitting = ref(false)
    const answerForm = ref({ answer: null })
    const timerStarted = ref(false)
    const currentStatus = ref('success')
    const lastResult = ref({
      show: false,
      correct: false,
      message: ''
    })
    const startTime = ref(0)
    const submitted = ref(false)
    const isFirstAnswer = ref(true)
    const showResultDialog = ref(false)
    const detailLoading = ref(false)
    const answerDetails = ref<any[]>([])
    const correctCount = ref(0)
    const accuracy = ref(0)
    
    // 获取习题集数据
    const fetchExpressions = async () => {
      loading.value = true
      try {
        const setId = route.params.id
        if (!setId) {
          ElMessage.error('练习ID无效')
          router.push('/practice')
          return
        }

        console.log('Fetching exercise set:', setId)  // 添加日志

        // 先获取习题集基本信息
        const response = await axios.get(`/api/exercise-set/${setId}`)
        const exerciseSet = response.data
        if (!exerciseSet) {
          ElMessage.error('习题集不存在')
          router.push('/practice')
          return
        }

        console.log('Exercise set:', exerciseSet)  // 添加日志
        
        // 获取表达式列表
        const expressionsResponse = await axios.get(`/api/exercise-set/${setId}/expressions`)
        expressions.value = expressionsResponse.data
        
        console.log('Expressions:', expressions.value)  // 添加日志

        if (!expressions.value || expressions.value.length === 0) {
          ElMessage.error('未找到练习题目')
          router.push('/practice')
          return
        }

        totalQuestions.value = expressions.value.length
        currentIndex.value = 0  // 确保从第一题开始

        // 设置当前题目
        if (expressions.value[0]) {
          currentExpression.value = expressions.value[0].expression_text
          console.log('Current expression:', currentExpression.value)  // 添加日志
        }

        // 设置时间限制
        remainingTime.value = exerciseSet.time_limit * 60
        startTime.value = Date.now()

        // 启动计时器
        if (!timerStarted.value) {
          startTimer()
          timerStarted.value = true
        }

        // 设置完初始题目后聚焦
        await focusInput()

      } catch (error: any) {
        console.error('获取习题失败:', error)
        ElMessage.error(error.response?.data?.error || '获取习题失败')
        router.push('/practice')
      } finally {
        loading.value = false
      }
    }
    
    // 格式化时间
    const formatTime = (seconds: number) => {
      if (!seconds) return '0'
      return seconds.toFixed(1)
    }
    
    // 格式化进度
    const format = (percentage: number) => {
      return `${currentIndex.value + 1}/${totalQuestions.value}`
    }
    
    // 记录练习结果
    const recordPractice = async (isTimeout: boolean) => {
      try {
        // 停止倒计时
        if (timer) {
          clearInterval(timer)
        }
        
        // 计算答题统计
        correctCount.value = expressions.value.filter(expr => 
          expr.userAnswer && Math.abs(expr.userAnswer - expr.answer) < 0.0001
        ).length
        
        accuracy.value = Number(((correctCount.value / totalQuestions.value) * 100).toFixed(1))
        
        // 准备答题详情数据
        answerDetails.value = expressions.value.map(expr => ({
          expression_text: expr.expression_text,
          answer: expr.answer,
          user_answer: expr.userAnswer || '-',
          is_correct: expr.userAnswer && Math.abs(expr.userAnswer - expr.answer) < 0.0001,
          answer_time: expr.answerTime || 0
        }))
        
        // 显示结果对话框
        showResultDialog.value = true
        
        return true
      } catch (error) {
        console.error('处理答题结果失败:', error)
        ElMessage.error('处理答题结果失败')
        return false
      }
    }

    // 在开始答题时记录时间
    const startAnswering = () => {
      startTime.value = Date.now()
    }
    
    // 添加一个专门的聚焦方法
    const focusInput = async () => {
      await nextTick()
      if (answerInput.value) {
        // 尝试多种方式聚焦
        answerInput.value.focus()
        const inputElement = answerInput.value.$el.querySelector('input')
        if (inputElement) {
          inputElement.focus()
        }
      }
    }

    // 修改提交答案函数
    const submitAnswer = async () => {
      if (isSubmitting.value) return
      
      try {
        await answerFormRef.value.validate()
        isSubmitting.value = true
        const answerTime = (Date.now() - startTime.value) / 1000
        
        // 提交原始数字答案，��进行格式化
        const response = await axios.post('/api/answer-record', {
          expression_id: expressions.value[currentIndex.value].expression_id,
          user_answer: Number(answerForm.value.answer),  // 保持为数字类型
          answer_time: answerTime
        })
        
        // 在显示和存储时才格式化为两位小数
        const formattedAnswer = Number(answerForm.value.answer).toFixed(2)
        expressions.value[currentIndex.value].userAnswer = formattedAnswer
        expressions.value[currentIndex.value].answerTime = answerTime
        expressions.value[currentIndex.value].is_correct = response.data.is_correct
        
        // 更新状态
        currentStatus.value = response.data.is_correct ? 'success' : 'error'
        
        // 只显示一个消息提示
        ElMessage({
          type: response.data.is_correct ? 'success' : 'error',
          message: response.data.is_correct ? '回答正确！' : '回答错误',
          duration: 1000,
          showClose: false
        })
        
        // 如果是最后一题
        if (currentIndex.value === totalQuestions.value - 1) {
          await recordPractice(false)
          clearProgress()
        } else {
          // 不是最后一题，继续下一题
          currentIndex.value++
          currentExpression.value = expressions.value[currentIndex.value].expression_text
          answerForm.value.answer = null
          startTime.value = Date.now()
          
          // 使用专门的聚焦方法
          await focusInput()
        }
        
      } catch (error: any) {
        if (!error.name?.includes('Validation')) {
          console.error('提交答案失败:', error)
          ElMessage.error('提交答案失败')
        }
      } finally {
        isSubmitting.value = false
      }
    }

    // 处理超时
    const handleTimeout = async () => {
      ElMessage.warning('时间到')
      await recordPractice(true)
      clearProgress()
      router.push('/practice')
    }

    // 倒计时
    let timer: number
    const startTimer = () => {
      if (timer) {
        clearInterval(timer)
      }
      
      timer = window.setInterval(() => {
        if (remainingTime.value > 0) {
          remainingTime.value--
          saveProgress() // 每秒保存一次进度
        } else {
          clearInterval(timer)
          handleTimeout()
        }
      }, 1000)
    }
    
    // 添加保存进度的函数
    const saveProgress = () => {
      const progress = {
        currentIndex: currentIndex.value,
        remainingTime: remainingTime.value,
        exerciseSetId: route.params.id
      }
      localStorage.setItem('practiceProgress', JSON.stringify(progress))
    }

    // 添加恢复进度的函数
    const restoreProgress = () => {
      const savedProgress = localStorage.getItem('practiceProgress')
      if (savedProgress) {
        const progress = JSON.parse(savedProgress)
        // 确保是同一个练习集
        if (progress.exerciseSetId === route.params.id) {
          currentIndex.value = progress.currentIndex
          remainingTime.value = progress.remainingTime
          return true
        }
      }
      return false
    }

    // 清除进度
    const clearProgress = () => {
      localStorage.removeItem('practiceProgress')
    }

    // 添加检查练习记录是否存在的函数
    const checkExistingRecord = async (exerciseSetId: string) => {
      try {
        const user = JSON.parse(localStorage.getItem('user') || '{}')
        const response = await axios.get(`/api/practice-record/${user.user_id}`, {
          params: {
            exercise_set_id: exerciseSetId,
            latest: true  // 添加参数获取最新记录
          }
        })
        return response.data.records.some((record: any) => 
          record.exercise_set_id === parseInt(exerciseSetId) && 
          new Date(record.completion_time).toDateString() === new Date().toDateString()
        )
      } catch (error) {
        console.error('检查练习记录失败:', error)
        return false
      }
    }

    // 添加跳转函数
    const goToHistory = () => {
      router.push('/history')
    }

    const startNewPractice = () => {
      router.push('/practice')
    }

    // 添加处理数字键盘输入的函数
    const handleKeyPress = (event: KeyboardEvent) => {
      // 如果当前正在提交答案，则不处理输入
      if (isSubmitting.value) return
      
      // 检查当前���点是否在输入框上
      const activeElement = document.activeElement
      const isInputFocused = activeElement && 
        (activeElement.tagName === 'INPUT' || 
         activeElement.classList.contains('el-input__inner'))
      
      // 如果输入框已经有焦点，不处理键盘事件
      if (isInputFocused) return
      
      // 获取按键的字符
      const key = event.key
      
      // 检查是否是数字键（0-9）、负号或退格键
      if (/^[0-9]$/.test(key) || key === 'Backspace' || key === '-') {
        event.preventDefault() // 阻止默认行为
        
        // 聚焦到输入框
        focusInput()
        
        // 如果是退格键
        if (key === 'Backspace') {
          if (answerForm.value.answer !== null) {
            const newValue = String(answerForm.value.answer).slice(0, -1)
            answerForm.value.answer = newValue ? Number(newValue) : null
          }
        } 
        // 如果是负号
        else if (key === '-') {
          if (answerForm.value.answer === null || answerForm.value.answer === undefined) {
            answerForm.value.answer = 0  // 先设置为0，以便后续添加负号
          }
          answerForm.value.answer = -Math.abs(answerForm.value.answer)  // 切换正负
        }
        // 如果是数字键
        else {
          const currentAnswer = answerForm.value.answer
          if (currentAnswer === null || currentAnswer === undefined) {
            answerForm.value.answer = Number(key)
          } else {
            const isNegative = currentAnswer < 0
            const absValue = Math.abs(currentAnswer)
            const newValue = String(absValue) + key
            if (Number(newValue) <= 100000) {
              answerForm.value.answer = isNegative ? -Number(newValue) : Number(newValue)
            }
          }
        }
      }
    }

    // 在组件挂载时添加键盘事件监听器
    onMounted(() => {
      document.addEventListener('keydown', handleKeyPress)
      fetchExpressions()
      focusInput()
    })

    // 在组件卸载时移除键盘事件监听器
    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeyPress)
      if (timer) {
        clearInterval(timer)
      }
    })

    // 添加 watch 来监听题目变化
    watch(currentIndex, async () => {
      await focusInput()
    })
    
    return {
      loading,
      currentIndex,
      totalQuestions,
      currentExpression,
      remainingTime,
      answerForm,
      answerFormRef,
      answerInput,
      isSubmitting,
      formatTime,
      format,
      submitAnswer,
      currentStatus,
      lastResult,
      handleTimeout,
      startAnswering,
      isFirstAnswer,
      submitted,
      showResultDialog,
      detailLoading,
      answerDetails,
      correctCount,
      accuracy,
      goToHistory,
      startNewPractice,
      focusInput,
      handleKeyPress
    }
  }
})
</script>

<style scoped>
.practice-detail {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  overflow: hidden;
}

.practice-card {
  width: 70%; /* 缩小卡片宽度 */
  max-width: 800px; /* 限制最大宽度 */
  height: 70vh; /* 缩小卡片高度 */
  margin: 0;
  display: flex;
  flex-direction: column;
  border-radius: 8px; /* 恢复圆角 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.practice-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-around; /* 改为 space-around 实现更好的垂直居中 */
  padding: 20px;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
}

.card-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
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
  color: #e6a23c;
  background-color: #fdf6ec;
}

.progress-section {
  width: 100%;
  padding: 0 20px;
}

.progress-bar {
  margin-bottom: 10px;
}

.progress-text {
  font-size: 18px;
  color: #606266;
  margin-top: 10px;
}

.expression-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin: 10px 0;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

.expression-container:hover {
  background-color: #eef2f6;
}

.expression {
  font-size: 48px;
  font-weight: bold;
  color: #303133;
  text-align: center;
  padding: 30px;
  letter-spacing: 4px;
}

.answer-section {
  width: 100%;
  max-width: 400px; /* 减小输入框最大宽度 */
  margin: 0 auto; /* 居中显示 */
  padding: 0 20px;
}

:deep(.el-input-group__append) {
  padding: 0;
}

:deep(.el-input-group__append button) {
  height: 50px; /* 稍微减小按钮高度 */
  margin: 0;
  border: none;
  padding: 0 25px;
  font-size: 16px;
}

:deep(.el-input__wrapper) {
  padding: 0 15px;
}

:deep(.el-input__inner) {
  height: 50px; /* 稍微减小输入框高度 */
  font-size: 20px;
  text-align: center;
  letter-spacing: 2px;
}

.result-message,
.fade-enter-active,
.fade-leave-active,
.fade-enter-from,
.fade-leave-to {
  display: none;
}

.statistics-section {
  margin: 20px 0;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.stat-card {
  text-align: center;
  padding: 15px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.stat-card.correct .stat-value {
  color: #67C23A;
}

.stat-label {
  margin-top: 8px;
  color: #606266;
}

.expressions-list {
  margin-top: 20px;
}

.expressions-list h3 {
  margin-bottom: 16px;
}

.dialog-footer {
  margin-top: 20px;
  text-align: center;
}
</style> 