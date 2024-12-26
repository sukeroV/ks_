<template>
  <div class="practice-container">
    <el-row :gutter="20">
      <!-- 左侧练习配置 -->
      <el-col :span="8">
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
            
            <el-form-item label="数值范围" required>
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-input-number
                    v-model="practiceForm.min_number"
                    :min="1"
                    :max="practiceForm.max_number"
                    :step="1"
                    :controls-position="'right'"
                    :keyboard="false"
                    placeholder="最小值"
                  />
                </el-col>
                <el-col :span="12">
                  <el-input-number
                    v-model="practiceForm.max_number"
                    :min="practiceForm.min_number"
                    :max="getMaxNumberByGrade"
                    :step="1"
                    :controls-position="'right'"
                    :keyboard="false"
                    placeholder="最大值"
                  />
                </el-col>
              </el-row>
            </el-form-item>
            
            <el-form-item label="运算符选择" required>
              <el-checkbox-group 
                v-model="practiceForm.operators" 
                @change="handleOperatorsChange"
              >
                <el-checkbox label="+" />
                <el-checkbox label="-" />
                <template v-if="userGrade > 2">
                  <el-checkbox label="×" />
                </template>
                <template v-if="userGrade > 4">
                  <el-checkbox label="÷" />
                </template>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="运算符数量" required>
              <div class="number-input-wrapper">
                <el-button 
                  @click="decreaseNumber('operator_count', 1, 1, getMaxOperatorsByGrade)"
                  :disabled="practiceForm.operator_count <= 1"
                >
                  <el-icon><Minus /></el-icon>
                </el-button>
                <span class="number-display">{{ practiceForm.operator_count }}</span>
                <el-button 
                  @click="increaseNumber('operator_count', 1, 1, getMaxOperatorsByGrade)"
                  :disabled="practiceForm.operator_count >= getMaxOperatorsByGrade"
                >
                  <el-icon><Plus /></el-icon>
                </el-button>
              </div>
            </el-form-item>
            
            <el-form-item label="括号题目数量" prop="bracket_expressions">
              <div class="number-input-wrapper">
                <el-button 
                  @click="decreaseNumber('bracket_expressions', 1, 0, getMaxBracketCount)"
                  :disabled="!canUseBrackets || practiceForm.bracket_expressions <= 0"
                >
                  <el-icon><Minus /></el-icon>
                </el-button>
                <span class="number-display">{{ practiceForm.bracket_expressions }}</span>
                <el-button 
                  @click="increaseNumber('bracket_expressions', 1, 0, getMaxBracketCount)"
                  :disabled="!canUseBrackets || practiceForm.bracket_expressions >= getMaxBracketCount"
                >
                  <el-icon><Plus /></el-icon>
                </el-button>
              </div>
            </el-form-item>
            
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
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧说明 -->
      <el-col :span="16">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <h3>练习说明</h3>
            </div>
          </template>
          
          <div class="info-content">
            <!-- 当前年级信息 -->
            <div class="grade-info">
              <el-alert
                :title="`当前年级：${userGrade}年级`"
                type="info"
                :closable="false"
                show-icon
              >
                <template #default>
                  <div class="grade-tip">
                    根据您的年级，系统会自动调整可用的运算符和数值范围
                  </div>
                </template>
              </el-alert>
            </div>

            <h4>年级对应说明</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="一、二年级">
                <div class="difficulty-detail">
                  - 只含1个运算符的算式
                  - 数值范围：1-20
                  - 运算符：加减
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="三、四年级">
                <div class="difficulty-detail">
                  - 最多2个运算符的算式
                  - 数值范围：1-50
                  - 运算符：加减乘
                  - 可包含括号
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="五、六年级">
                <div class="difficulty-detail">
                  - 最多3个运算符的算式
                  - 数值范围：1-100
                  - 运算符：加减乘除
                  - 可包含括号
                </div>
              </el-descriptions-item>
            </el-descriptions>

            <h4>注意事项：</h4>
            <el-alert
              title="请在规定时间内完成练习"
              type="warning"
              :closable="false"
              show-icon
            />
            <el-alert
              title="除法运算结果精确到小数点后2位"
              type="info"
              :closable="false"
              show-icon
            />
            <el-alert
              title="括号题目数量不能超过总题目数量"
              type="info"
              :closable="false"
              show-icon
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Minus } from '@element-plus/icons-vue'
import axios from 'axios'

export default defineComponent({
  name: 'Practice',
  components: {
    Plus,
    Minus
  },
  setup() {
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
    
    // 根据年级获取最大数值
    const getMaxNumberByGrade = computed(() => {
      const grade = userGrade.value
      if (grade <= 2) return 20
      if (grade <= 4) return 50
      return 100
    })

    // 根据年级获取最大运算符数量
    const getMaxOperatorsByGrade = computed(() => {
      const grade = userGrade.value
      // 限制运算符数量不能超过已选择的运算符数量
      const maxByGrade = grade <= 2 ? 1 : grade <= 4 ? 2 : 3
      return Math.min(maxByGrade, practiceForm.operators.length)
    })

    const practiceForm = reactive({
      total_expressions: 5,
      bracket_expressions: 0,
      time_limit: 10,
      operators: ['+', '-'],
      operator_count: 1,
      min_number: 1,
      max_number: 20
    })

    // 根据年级初始化运算符
    const initOperatorsByGrade = () => {
      const grade = userGrade.value
      if (grade <= 2) {
        practiceForm.operators = ['+', '-']
        practiceForm.operator_count = 1
      } else if (grade <= 4) {
        practiceForm.operators = ['+', '-', '×']
        practiceForm.operator_count = Math.min(practiceForm.operator_count, 2)
      } else {
        practiceForm.operators = ['+', '-', '×', '÷']
      }
    }

    // 在组件挂载时初始化
    onMounted(() => {
      const savedConfig = localStorage.getItem('practiceConfig')
      if (savedConfig) {
        const config = JSON.parse(savedConfig)
        // 根据年级限制数值范围
        const maxNumber = getMaxNumberByGrade.value
        config.max_number = Math.min(config.max_number, maxNumber)
        config.min_number = Math.min(config.min_number, config.max_number)
        
        // 根据年级过滤运算符
        const grade = userGrade.value
        const allowedOperators = ['+', '-']
        if (grade > 2) allowedOperators.push('×')
        if (grade > 4) allowedOperators.push('÷')
        
        config.operators = config.operators.filter(op => allowedOperators.includes(op))
        if (config.operators.length === 0) {
          config.operators = ['+', '-']
        }
        
        // 限制运算符数量
        if (grade <= 2) {
          config.operator_count = 1
        } else if (grade <= 4) {
          config.operator_count = Math.min(config.operator_count, 2)
        } else {
          config.operator_count = Math.min(config.operator_count, 3)
        }
        
        Object.assign(practiceForm, config)
      } else {
        // 初始化时设置合适的默认值
        practiceForm.max_number = Math.min(20, getMaxNumberByGrade.value)
        initOperatorsByGrade()
      }
    })
    // 开始练习
    const startPractice = async () => {
      try {
        // 检查并自动调整范围，只有当包含加减法时才需要调整
        const hasAddOrSub = practiceForm.operators.some(op => op === '+' || op === '-')
        if (hasAddOrSub) {
          const minRequired = practiceForm.min_number + practiceForm.total_expressions
          if (practiceForm.max_number <= minRequired) {
            // 自动调整最大值
            practiceForm.max_number = minRequired + 1
            ElMessage.info(`已自动调整最大值为${minRequired + 1}，以满足题目生成要求`)
          }
        } else {
          // 对于纯乘除法，只需要确保范围内有足够的数字组合
          const range = practiceForm.max_number - practiceForm.min_number + 1
          if (range < 2) {  // 至少需要2个不同的数字
            practiceForm.max_number = practiceForm.min_number + 2
            ElMessage.info(`已自动调整最大值以确保有足够的数字组合`)
          }
        }

        await practiceFormRef.value.validate(async (valid: boolean) => {
          if (valid) {
            const user = JSON.parse(localStorage.getItem('user') || '{}')
            
            const response = await axios.post('/api/exercise-set', {
              ...practiceForm,
              operators: practiceForm.operators,
              user_id: user.user_id
            })
            const exerciseSetId = response.data.exercise_set_id
            router.push(`/practice/${exerciseSetId}`)
          }
        })
      } catch (error) {
        console.error('创建练习失败:', error)
        ElMessage.error('创建练习失败')
      }
    }
    
    // 判断是否可以使用括号
    const canUseBrackets = computed(() => {
      // 只有当运算符数量大于1且包含乘除法时才允许使用括号
      const hasMulOrDiv = practiceForm.operators.some(op => op === '×' || op === '÷')
      return practiceForm.operator_count > 1 && hasMulOrDiv
    })

    // 监听总题目数量变化
    watch(() => practiceForm.total_expressions, (newValue) => {
      // 确保括号题目数量不超过总题目数量
      if (practiceForm.bracket_expressions > newValue) {
        practiceForm.bracket_expressions = newValue
      }
    })

    // 获取最大括号题目数量
    const getMaxBracketCount = computed(() => {
      if (!canUseBrackets.value) return 0
      return Math.min(practiceForm.total_expressions, 
                     Math.floor(practiceForm.total_expressions)) // 最多占总题数的一半
    })

    // 处理括号题目数量变化
    const handleBracketCountChange = (value: number) => {
      // 确保不超过总题目数量
      if (value > practiceForm.total_expressions) {
        practiceForm.bracket_expressions = practiceForm.total_expressions
      }
    }

    // 处理运算符变化
    const handleOperatorsChange = () => {
      // 确保至少选择一个运算符
      if (practiceForm.operators.length === 0) {
        practiceForm.operators = ['+']
        ElMessage.warning('至少需要选择一个运算符')
        return
      }
      
      // 限制运算符数量不能超过选择的运算符数量
      if (practiceForm.operator_count > practiceForm.operators.length) {
        practiceForm.operator_count = practiceForm.operators.length
      }
      
      // 如果没有乘除法，清空括号题目数量
      const hasMulOrDiv = practiceForm.operators.some(op => op === '×' || op === '÷')
      if (!hasMulOrDiv) {
        practiceForm.bracket_expressions = 0
      }
      
      // 如果  算符不足两个，限制运算符数量为1
      if (practiceForm.operators.length < 2) {
        practiceForm.operator_count = 1
        practiceForm.bracket_expressions = 0
      }
    }

    // 处理运算符数量变化
    const handleOperatorCountChange = (value: number) => {
      if (value <= 1) {
        practiceForm.bracket_expressions = 0
      }
    }

    // 监听运算符数量变化
    watch(() => practiceForm.operator_count, (newValue) => {
      if (newValue <= 1) {
        practiceForm.bracket_expressions = 0
      }
    })

    // 监听运算符选择变化
    watch(() => practiceForm.operators, (newValue) => {
      // 根据选择的运算符数限制operator_count的最大值
      const maxOperators = Math.min(newValue.length, getMaxOperatorsByGrade.value)
      if (practiceForm.operator_count > maxOperators) {
        practiceForm.operator_count = maxOperators
      }
      
      if (newValue.length < 2) {
        practiceForm.operator_count = 1
        practiceForm.bracket_expressions = 0
      }
    })

    // 验证表单规则
    const validateRange = (rule: any, value: any, callback: any) => {
      // 获取最小值和最大值
      const minNumber = practiceForm.min_number
      const maxNumber = practiceForm.max_number
      const totalQuestions = practiceForm.total_expressions
      
      // 检查范围是否足够大
      if (maxNumber - minNumber + 1 < totalQuestions) {
        callback(new Error(`数值范围(${maxNumber - minNumber + 1})必须大于或等于题目数量(${totalQuestions})`))
      } else {
        callback()
      }
    }

    const rules = {
      total_expressions: [
        { required: true, message: '请输入题目数量', trigger: 'blur' },
        { type: 'number', min: 1, message: '题目数量必须大于0', trigger: 'blur' },
        { 
          validator: (rule: any, value: any, callback: any) => {
            const range = practiceForm.max_number - practiceForm.min_number + 1
            if (range < value) {
              callback(new Error(`题目数量(${value})不能大于数值范围(${range})`))
            } else {
              callback()
            }
          },
          trigger: ['blur', 'change']
        }
      ],
      min_number: [
        { required: true, message: '请输入最小值', trigger: 'blur' },
        { type: 'number', message: '必须是数字', trigger: 'blur' }
      ],
      max_number: [
        { required: true, message: '请输入最大值', trigger: 'blur' },
        { type: 'number', message: '必须是数字', trigger: 'blur' },
        {
          validator: (rule: any, value: any, callback: any) => {
            const range = value - practiceForm.min_number + 1
            if (range < practiceForm.total_expressions) {
              callback(new Error(`数值范围(${range})必须大于或等于题目数量(${practiceForm.total_expressions})`))
            } else {
              callback()
            }
          },
          trigger: ['blur', 'change']
        }
      ],
      bracketCount: [
        { 
          validator: (rule: any, value: number, callback: Function) => {
            if (value > practiceForm.total_expressions) {
              callback(new Error('括号题目数量不能超过总题目数量'))
            } else {
              callback()
            }
          }, 
          trigger: 'change' 
        }
      ]
    }

    // 监听数值范围和题目数量变化
    watch([
      () => practiceForm.min_number,
      () => practiceForm.max_number,
      () => practiceForm.total_expressions
    ], ([min, max, total]) => {
      if (min !== undefined && max !== undefined && total !== undefined) {
        const minRequired = min + total
        if (max <= minRequired) {
          // 自动将最大值调整为符合要求的值
          practiceForm.max_number = minRequired + 1
          ElMessage.info(`已自动调整最大值为${minRequired + 1}，以满足题目生成要求`)
        }
      }
    }, { immediate: true })

    // 处理最大值变化
    const handleMaxNumberChange = (value: number) => {
      const minRequired = practiceForm.min_number + practiceForm.total_expressions
      if (value <= minRequired) {
        // 自动调整为符合要求的值
        practiceForm.max_number = minRequired + 1
      }
    }

    // 处理最小值变化
    const handleMinNumberChange = (value: number) => {
      const minRequired = value + practiceForm.total_expressions
      if (practiceForm.max_number <= minRequired) {
        // 自动调整最大值
        practiceForm.max_number = minRequired + 1
      }
    }

    // 处理题目数量变化
    const handleTotalExpressionsChange = (value: number) => {
      const minRequired = practiceForm.min_number + value
      if (practiceForm.max_number <= minRequired) {
        // 自动调整最大值
        practiceForm.max_number = minRequired + 1
      }
    }

    // 增加数值的方法
    const increaseNumber = (field: string, step: number, min: number, max: number) => {
      const newValue = practiceForm[field] + step
      if (newValue <= max) {
        practiceForm[field] = newValue
        if (field === 'operator_count') {
          handleOperatorCountChange(newValue)
        } else if (field === 'bracket_expressions') {
          handleBracketCountChange(newValue)
        }
      }
    }

    // 减少数值的方法
    const decreaseNumber = (field: string, step: number, min: number, max: number) => {
      const newValue = practiceForm[field] - step
      if (newValue >= min) {
        practiceForm[field] = newValue
        if (field === 'operator_count') {
          handleOperatorCountChange(newValue)
        } else if (field === 'bracket_expressions') {
          handleBracketCountChange(newValue)
        }
      }
    }

    // 在 setup 函数中添加对整个表单的监听
    watch(
      () => ({ ...practiceForm }), // 监听整个表单对象
      (newConfig) => {
        // 保存配置到本地存储
        localStorage.setItem('practiceConfig', JSON.stringify(newConfig))
      },
      { deep: true } // 深度监听
    )

    return {
      practiceForm,
      practiceFormRef,
      startPractice,
      userGrade,
      getMaxNumberByGrade,
      getMaxOperatorsByGrade,
      canUseBrackets,
      getMaxBracketCount,
      handleOperatorsChange,
      handleOperatorCountChange,
      handleBracketCountChange,
      rules,
      initOperatorsByGrade,
      increaseNumber,
      decreaseNumber,
      Plus,
      Minus
    }
  }
})
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
</style> 

<!--  -->

<!--  -->