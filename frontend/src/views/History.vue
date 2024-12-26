<template>
  <div class="history-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>练习历史</h2>
        </div>
      </template>

      <el-table 
        v-loading="loading"
        :data="practiceRecords"
        style="width: 100%"
      >
        <el-table-column label="练习时间" min-width="180">
          <template #default="{ row }">
            {{ formatDate(row.completion_time) }}
          </template>
        </el-table-column>

        <el-table-column label="题目数量" width="100">
          <template #default="{ row }">
            {{ row.total_expressions }}题
          </template>
        </el-table-column>

        <el-table-column label="括号题目" width="100">
          <template #default="{ row }">
            {{ row.bracket_expressions }}题
          </template>
        </el-table-column>

        <el-table-column label="时间限制" width="100">
          <template #default="{ row }">
            {{ row.time_limit }}分钟
          </template>
        </el-table-column>

        <el-table-column label="运算符" min-width="120">
          <template #default="{ row }">
            <el-tag 
              v-for="op in row.operators?.split(',')" 
              :key="op"
              size="small"
              class="operator-tag"
            >
              {{ op }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="数值范围" min-width="120">
          <template #default="{ row }">
            {{ row.min_number }} - {{ row.max_number }}
          </template>
        </el-table-column>

        <el-table-column label="运算符数量" width="100">
          <template #default="{ row }">
            {{ row.operator_count }}个
          </template>
        </el-table-column>

        <el-table-column label="准确率" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="getAccuracyType(row.accuracy)"
              size="small"
            >
              {{ row.accuracy }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="答题用时" width="120">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
            <el-tag 
              v-if="row.is_timeout" 
              type="warning" 
              size="small" 
              style="margin-left: 4px"
            >
              超时
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link
              @click="viewDetail(row.exercise_set_id)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="练习详情"
      width="80%"
    >
      <div v-loading="detailLoading">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="练习时间">
            {{ formatDate(currentDetail?.create_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="题目数量">
            {{ currentDetail?.total_expressions }}题
          </el-descriptions-item>
          <el-descriptions-item label="括号题目">
            {{ currentDetail?.bracket_expressions }}题
          </el-descriptions-item>
          <el-descriptions-item label="时间限制">
            {{ currentDetail?.time_limit }}分钟
          </el-descriptions-item>
          <el-descriptions-item label="运算符">
            <el-tag 
              v-for="op in currentDetail?.operators?.split(',')" 
              :key="op"
              size="small"
              class="operator-tag"
            >
              {{ op }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="数值范围">
            {{ currentDetail?.min_number }} - {{ currentDetail?.max_number }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 统计信息部分 -->
        <div class="statistics-section">
          <h3>练习统计</h3>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-value">{{ statistics.total }}</div>
                <div class="stat-label">总题数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card correct">
                <div class="stat-value">{{ statistics.correct }}</div>
                <div class="stat-label">正确</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card incorrect">
                <div class="stat-value">{{ statistics.incorrect }}</div>
                <div class="stat-label">错误</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-value">{{ statistics.accuracy }}</div>
                <div class="stat-label">正确率</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 题目列表 -->
        <div class="expressions-list">
          <h3>题目列表</h3>
          <el-table :data="expressionsList" border style="width: 100%">
            <el-table-column label="题目" prop="expression_text" />
            <el-table-column label="正确答案" prop="answer" width="120" />
            <el-table-column label="你的答案" prop="user_answer" width="120" />
            <el-table-column label="是否正确" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_correct ? 'success' : 'danger'">
                  {{ row.is_correct ? '正确' : '错误' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

export default defineComponent({
  name: 'History',
  setup() {
    const loading = ref(false)
    const practiceRecords = ref([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    
    const dialogVisible = ref(false)
    const detailLoading = ref(false)
    const currentDetail = ref<any>(null)
    const expressionsList = ref([])
    const statistics = ref({
      total: 0,
      correct: 0,
      incorrect: 0,
      accuracy: '0%'
    })

    // 格式化日期
    const formatDate = (dateStr: string) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleString()
    }

    // 获取练习记录
    const fetchRecords = async () => {
      loading.value = true
      try {
        const user = JSON.parse(localStorage.getItem('user') || '{}')
        const response = await axios.get('/api/practice-records', {
          params: {
            user_id: user.user_id,
            page: currentPage.value,
            size: pageSize.value
          }
        })
        
        // 处理每条记录
        practiceRecords.value = response.data.records.map((record: any) => ({
          ...record,
          accuracy: record.total_expressions > 0 
            ? `${((record.correct_count / record.total_expressions) * 100).toFixed(1)}%`
            : '0.0%'
        }))
        total.value = response.data.total
      } catch (error: any) {
        console.error('获取练习记录失败:', error)
        ElMessage.error('获取练习记录失败')
      } finally {
        loading.value = false
      }
    }

    // 查看详情
    const viewDetail = async (exerciseSetId: number) => {
      dialogVisible.value = true
      detailLoading.value = true
      try {
        // 获取练习详情和答题记录
        const response = await axios.get(`/api/exercise-set/${exerciseSetId}/answers`)
        
        // 更新练习集信息
        currentDetail.value = response.data.exercise_set
        
        // 更新表达式列表
        expressionsList.value = response.data.expressions
        
        // 更新统计信息
        statistics.value = response.data.statistics
        
      } catch (error: any) {
        ElMessage.error('获取详情失败')
      } finally {
        detailLoading.value = false
      }
    }

    // 分页处理
    const handleSizeChange = (val: number) => {
      pageSize.value = val
      fetchRecords()
    }

    const handleCurrentChange = (val: number) => {
      currentPage.value = val
      fetchRecords()
    }

    // 根据准确率返回不同的标签类型
    const getAccuracyType = (accuracy: string) => {
      const value = parseFloat(accuracy)
      if (value >= 90) return 'success'
      if (value >= 60) return 'warning'
      return 'danger'
    }

    // 格式化答题用时
    const formatDuration = (seconds: number | null) => {
      if (seconds === null || seconds === undefined) return '-'
      
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = Math.floor(seconds % 60)
      
      if (minutes === 0) {
        return `${remainingSeconds}秒`
      }
      return `${minutes}分${remainingSeconds}秒`
    }

    onMounted(() => {
      fetchRecords()
    })

    return {
      loading,
      practiceRecords,
      currentPage,
      pageSize,
      total,
      dialogVisible,
      detailLoading,
      currentDetail,
      expressionsList,
      statistics,
      formatDate,
      viewDetail,
      handleSizeChange,
      handleCurrentChange,
      getAccuracyType,
      formatDuration
    }
  }
})
</script>

<style scoped>
.history-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.operator-tag {
  margin-right: 4px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.expressions-list {
  margin-top: 20px;
}

.expressions-list h3 {
  margin-bottom: 16px;
}

:deep(.el-descriptions) {
  margin-bottom: 20px;
}

:deep(.el-descriptions__label) {
  width: 120px;
  font-weight: bold;
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

.stat-card.incorrect .stat-value {
  color: #F56C6C;
}

.stat-label {
  margin-top: 8px;
  color: #606266;
}
</style> 