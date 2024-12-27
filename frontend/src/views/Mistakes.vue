<template>
  <div class="mistakes-container">
    <!-- 加载状态 -->
    <el-loading 
      v-if="loading"
      text="加载中..."
      background="rgba(255, 255, 255, 0.8)"
      :fullscreen="true"
    />

    <!-- 错题列表 -->
    <el-card class="mistakes-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h2>错题本</h2>
            <el-tag type="info" class="count-tag">
              共 {{ total }} 道错题
            </el-tag>
          </div>
          <div class="header-actions">
            <el-dropdown @command="handleExport" trigger="click">
              <el-button type="success">
                <el-icon><Download /></el-icon>
                导出
                <el-icon class="el-icon--right"><CaretBottom /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="word">导出为Word</el-dropdown-item>
                  <el-dropdown-item command="csv">导出为CSV</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            
            <el-button 
              type="primary"
              :icon="Plus"
              @click="createPracticeFromSelected"
              :disabled="!selectedMistakes.length"
            >
              生成练习
            </el-button>
            <el-button 
              :icon="Refresh" 
              circle 
              @click="fetchMistakes"
              :loading="loading"
            />
          </div>
        </div>
      </template>

      <!-- 筛选器 -->
      <div class="filters">
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          :shortcuts="dateShortcuts"
          value-format="YYYY-MM-DD"
        />

        <el-input
          v-model="filters.search"
          placeholder="搜索算式..."
          clearable
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-switch
          v-model="filters.showExported"
          active-text="显示已导出"
          inactive-text="仅显示未导出"
          @change="handleShowExportedChange"
        />
      </div>

      <!-- 错题列表 -->
      <template v-if="mistakes && mistakes.length > 0">
        <el-table
          :data="mistakes"
          style="width: 100%"
          :max-height="tableHeight"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="id" label="ID" width="80">
            <template #default="scope">
              <el-tag size="small" type="info">{{ scope.row.id }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="completion_time" label="日期" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.completion_time) }}
            </template>
          </el-table-column>
          
          <el-table-column prop="expression" label="算式" min-width="200">
            <template #default="scope">
              <span class="expression-text">{{ scope.row.expression }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="correct_answer" label="正确答案" width="120">
            <template #default="scope">
              <el-tag type="success">{{ scope.row.correct_answer }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="user_answer" label="你的答案" width="120">
            <template #default="scope">
              <el-tag type="danger">{{ scope.row.user_answer }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="difficulty" label="难度" width="100">
            <template #default="scope">
              <el-tag :type="getDifficultyType(scope.row.difficulty)">
                {{ getDifficultyLabel(scope.row.difficulty) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" fixed="right" width="150">
            <template #default="scope">
              <el-button 
                type="primary" 
                link
                @click="practiceAgain(scope.row)"
              >
                重新练习
              </el-button>
              <el-button 
                type="danger" 
                link
                @click="removeMistake(scope.row)"
              >
                移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页组件 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </template>

      <!-- 空状态 -->
      <el-empty
        v-else
        description="暂无错题记录"
      >
        <template #image>
          <el-icon :size="60" color="#909399"><DocumentDelete /></el-icon>
        </template>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, 
  Plus, 
  Search,
  Download,
  CaretBottom,
  DocumentDelete
} from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const mistakes = ref<any[]>([])
const selectedMistakes = ref<any[]>([])
const tableHeight = ref('calc(100vh - 280px)')

// 分页相关的变量
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 筛选条件
const filters = ref({
  dateRange: null,
  search: '',
  showExported: false
})

// 日期快捷选项
const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近一月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setMonth(start.getMonth() - 1)
      return [start, end]
    }
  }
]

// 获取错题记录
const fetchMistakes = async () => {
  try {
    loading.value = true
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      show_exported: filters.value.showExported,
      search: filters.value.search || '',
      start_date: filters.value.dateRange?.[0] || '',
      end_date: filters.value.dateRange?.[1] || ''
    }
    
    console.log('Fetching mistakes with params:', params)
    
    const response = await axios.get(`/api/error-records/${user.user_id}`, { params })
    
    if (response.data.items) {
      mistakes.value = response.data.items
      total.value = response.data.total
    } else {
      mistakes.value = []
      total.value = 0
    }
  } catch (error: any) {
    console.error('获取错题失败:', error)
    ElMessage.error(error.response?.data?.error || '获取错题失败')
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (isoDate: string) => {
  const date = new Date(isoDate)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化用时
const formatTime = (seconds: number) => {
  return seconds.toFixed(1)
}

// 处理选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedMistakes.value = selection
}

// 从选中的错题创建练习
const createPracticeFromSelected = async () => {
  try {
    loading.value = true
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    
    const response = await axios.post('/api/practice-from-mistakes', {
      user_id: user.user_id,
      mistake_ids: selectedMistakes.value.map(m => m.id)
    })
    
    router.push(`/practice/${response.data.exercise_set_id}`)
  } catch (error) {
    console.error('创建练习失败:', error)
    ElMessage.error('创建练习失败')
  } finally {
    loading.value = false
  }
}

// 移除错题
const removeMistake = async (mistake: any) => {
  try {
    await ElMessageBox.confirm(
      '确定要从错题本中移除这道题吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await axios.delete(`/api/error-records/${mistake.id}`)
    ElMessage.success('已移除')
    await fetchMistakes()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除错题失败:', error)
      ElMessage.error('移除失败')
    }
  }
}

// 添加缺失的难度判断函数
const getDifficultyType = (difficulty: string) => {
  const types: Record<string, string> = {
    simple: 'success',
    medium: 'warning',
    hard: 'danger'
  }
  return types[difficulty] || 'info'
}

const getDifficultyLabel = (difficulty: string) => {
  const labels: Record<string, string> = {
    simple: '简单',
    medium: '中等',
    hard: '困难'
  }
  return labels[difficulty] || '未知'
}

// 添加缺失的重新练习函数
const practiceAgain = async (mistake: any) => {
  try {
    loading.value = true
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    
    const response = await axios.post('/api/practice-from-mistakes', {
      user_id: user.user_id,
      mistake_ids: [mistake.id]
    })
    
    router.push(`/practice/${response.data.exercise_set_id}`)
  } catch (error) {
    console.error('创建练习失败:', error)
    ElMessage.error('创建练习失败')
  } finally {
    loading.value = false
  }
}

// 修改导出处理函数
const handleExport = async (type: string) => {
  try {
    if (selectedMistakes.value.length === 0) {
      ElMessage.warning('请先选择要导出的错题')
      return
    }

    loading.value = true
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    
    // 获取要导出的错题信息，移除错误次数
    const exportData = selectedMistakes.value.map(item => ({
      id: item.id,
      expression: item.expression,
      correct_answer: item.correct_answer,
      user_answer: item.user_answer,
      completion_time: formatDate(item.completion_time)
    }))
    
    // 发起导出请求
    const response = await axios.post(
      `/api/error-records/${user.user_id}/export`, 
      {
        type,
        mistakes: exportData
      },
      {
        responseType: 'blob'
      }
    )

    // 创建下载链接
    const blob = new Blob([response.data], {
      type: type === 'word' 
        ? 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        : 'text/csv;charset=utf-8'
    })
    
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(blob)
    link.download = `错题本_${new Date().toLocaleDateString()}.${type === 'word' ? 'docx' : 'csv'}`
    link.click()
    window.URL.revokeObjectURL(link.href)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    loading.value = false
  }
}

// 处理显示已导出切换
const handleShowExportedChange = () => {
  currentPage.value = 1  // 重置页码
  fetchMistakes()
}

// 分页处理函数
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  fetchMistakes()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchMistakes()
}

// 修改筛选条件变化的处理
watch(
  () => [
    filters.value.search,
    filters.value.dateRange,
    filters.value.showExported
  ],
  () => {
    currentPage.value = 1 // 重置到第一页
    fetchMistakes()
  },
  { deep: true }
)

onMounted(() => {
  fetchMistakes()
})
</script>

<style scoped>
.mistakes-container {
  padding: 20px;
  min-height: calc(100vh - 60px);
  background-color: #f5f7fa;
}

.mistakes-card {
  min-height: calc(100vh - 100px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.count-tag {
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filters {
  margin-bottom: 20px;
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: center;  /* 添加垂直居中对齐 */
}

.search-input {
  width: 200px;
}

.expression-text {
  font-family: 'Courier New', Courier, monospace;
  font-size: 16px;
  color: #303133;
}

:deep(.el-table) {
  margin-top: 20px;
}

:deep(.el-loading-mask) {
  z-index: 1000;
}

:deep(.el-loading-text) {
  font-size: 16px;
  margin-top: 10px;
}

:deep(.el-switch) {
  margin-left: auto;  /* 将开关推到右侧 */
}
</style> 