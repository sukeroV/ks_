<template>
  <div class="home-container">
    <!-- 添加全局加载状态 -->
    <el-loading 
      v-if="isUpdating"
      text="正在更新数据..."
      background="rgba(255, 255, 255, 0.8)"
      :fullscreen="true"
    />
    
    <el-row :gutter="20">
      <!-- 左侧统计卡片 -->
      <el-col :span="6">
        <el-card class="welcome-card">
          <template #header>
            <div class="welcome-header">
              <h2>{{ greeting }}</h2>
            </div>
          </template>
          
          <div class="user-info">
            <el-avatar :size="64" :src="avatarUrl">{{ userName?.charAt(0) }}</el-avatar>
            <h3>{{ userName }}</h3>
            <div class="grade">{{ userGrade }}年级</div>
          </div>
          
          <div class="statistics-list">
            <div class="stat-item">
              <div class="stat-label">总练习次数</div>
              <div class="stat-value total">{{ totalPractices }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">平均正确率</div>
              <div class="stat-value accuracy">{{ averageAccuracy }}%</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">累计练习时间</div>
              <div class="stat-value time">{{ totalTime }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧图表区域 -->
      <el-col :span="18">
        <el-row :gutter="20">
          <!-- 趋势图和答题数量 -->
          <el-col :span="24">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card class="chart-card">
                  <template #header>
                    <div class="card-header">
                      <h3>正确率趋势</h3>
                      <!-- 添加刷新按钮 -->
                      <el-button 
                        :icon="Refresh" 
                        circle 
                        size="small"
                        @click="refreshData"
                        :loading="isUpdating"
                      />
                    </div>
                  </template>
                  <div class="chart-container">
                    <div ref="accuracyChart" style="width: 100%; height: 400px"></div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card class="chart-card">
                  <template #header>
                    <div class="card-header">
                      <h3>答题数量</h3>
                    </div>
                  </template>
                  <div class="chart-container">
                    <div ref="practiceCountChart" style="width: 100%; height: 400px"></div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </el-col>

          <!-- 运算符分析和用时分布 -->
          <el-col :span="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <h3>运算符正确率分析</h3>
                </div>
              </template>
              <div class="chart-container">
                <div ref="operatorChart" style="width: 100%; height: 400px"></div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <h3>答题用时分布</h3>
                </div>
              </template>
              <div class="chart-container">
                <div ref="timeDistChart" style="width: 100%; height: 400px"></div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import { Refresh } from '@element-plus/icons-vue'

export default defineComponent({
  name: 'Home',
  setup() {
    const router = useRouter()
    const accuracyChart = ref<HTMLElement | null>(null)
    const operatorChart = ref<HTMLElement | null>(null)
    const timeDistChart = ref<HTMLElement | null>(null)
    const practiceCountChart = ref<HTMLElement | null>(null)
    const trendTimeRange = ref('week')
    const isUpdating = ref(false)
    const cachedData = ref<any>(null)

    const userName = ref('')
    const userGrade = ref('')
    const totalPractices = ref(0)
    const averageAccuracy = ref(0)
    const totalTime = ref('0小时')

    // 获取问候语
    const getGreeting = () => {
      const hour = new Date().getHours()
      if (hour < 6) return '夜深了'
      if (hour < 9) return '早上好'
      if (hour < 12) return '上午好'
      if (hour < 14) return '中午好'
      if (hour < 17) return '下午好'
      if (hour < 19) return '傍晚好'
      return '晚上好'
    }
    const greeting = ref(getGreeting())

    // 获取用户统计数据
    const fetchUserStats = async (useCache = true) => {
      try {
        const user = JSON.parse(localStorage.getItem('user') || '{}')
        
        // 如果使用缓存且有缓存数据，先显示缓存数据
        if (useCache && cachedData.value) {
          initCharts(cachedData.value)
        }

        // 开始更新数据
        isUpdating.value = true
        const response = await axios.get(`/api/user/${user.user_id}/statistics`)
        const stats = response.data
        
        // 更新缓存
        cachedData.value = stats
        
        // 更新显示
        userName.value = user.name
        userGrade.value = user.grade
        totalPractices.value = stats.total_practices
        averageAccuracy.value = stats.average_accuracy.toFixed(1)
        totalTime.value = formatPracticeTime(stats.total_time)

        // 初始化图表
        initCharts(stats)
      } catch (error) {
        console.error('获取用户统计数据失败:', error)
        ElMessage.error('获取数据失败，请稍后重试')
      } finally {
        isUpdating.value = false
      }
    }

    // 初始化所有图表
    const initCharts = (data: any) => {
      initAccuracyChart(data.week_trend)
      initPracticeCountChart(data.week_trend)
      initOperatorChart(data.operator_accuracy)
      initTimeDistChart(data.time_distribution)
    }

    // 刷新数据
    const refreshData = () => {
      fetchUserStats(false)  // 不使用缓存强制刷新
    }

    // 修改趋势图表初始化
    const initAccuracyChart = (data: any) => {
      if (!accuracyChart.value) return
      
      const chart = echarts.init(accuracyChart.value)
      const option: EChartsOption = {
        grid: {
          top: '10%',
          right: '5%',
          bottom: '10%',
          left: '5%',
          containLabel: true
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: data.map((item: any) => item.date),
          axisLabel: {
            interval: 0,
            rotate: 30
          }
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [
          {
            name: '正确率',
            type: 'line',
            data: data.map((item: any) => item.accuracy),
            smooth: true,
            lineStyle: {
              color: '#409EFF'
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(64,158,255,0.3)' },
                { offset: 1, color: 'rgba(64,158,255,0.1)' }
              ])
            }
          }
        ]
      }
      chart.setOption(option)
    }

    // 添加答题数量图表初始化
    const initPracticeCountChart = (data: any) => {
      if (!practiceCountChart.value) return
      
      const chart = echarts.init(practiceCountChart.value)
      const option: EChartsOption = {
        grid: {
          top: '10%',
          right: '5%',
          bottom: '10%',
          left: '5%',
          containLabel: true
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: data.map((item: any) => item.date),
          axisLabel: {
            interval: 0,
            rotate: 30
          }
        },
        yAxis: {
          type: 'value',
          minInterval: 1
        },
        series: [
          {
            name: '答题数量',
            type: 'bar',
            data: data.map((item: any) => item.count),
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 1, 0, 0, [
                { offset: 0, color: '#83bff6' },
                { offset: 0.5, color: '#188df0' },
                { offset: 1, color: '#188df0' }
              ])
            }
          }
        ]
      }
      chart.setOption(option)
    }

    // 修改运算符分析图表初始化
    const initOperatorChart = (data: any) => {
      if (!operatorChart.value) return
      
      const chart = echarts.init(operatorChart.value)
      
      // 计算总体准确率
      const totalAccuracy = data.reduce((acc: number, curr: any) => acc + curr.value, 0) / data.length

      const option: EChartsOption = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c}%'
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center',
          formatter: (name: string) => {
            const item = data.find((d: any) => d.name === name)
            return `${name}: ${item?.value}%`
          }
        },
        series: [
          {
            name: '运算符正确率',
            type: 'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 20,
                fontWeight: 'bold',
                formatter: '{b}: {c}%'
              }
            },
            data: data,
            // 添加中心文本
            labelLine: {
              show: false
            },
            // 中心文本配置
            title: {
              show: true,
              text: `${totalAccuracy.toFixed(1)}%\n总体准确率`,
              left: 'center',
              top: 'middle',
              textStyle: {
                fontSize: 20,
                color: '#303133',
                fontWeight: 'bold',
                lineHeight: 30
              }
            }
          }
        ],
        // 添加中心文本
        graphic: [
          {
            type: 'text',
            left: 'center',
            top: '50%',
            style: {
              text: '',
              textAlign: 'center',
              fill: '#303133',
              fontSize: 20,
              fontWeight: 'bold'
            }
          }
        ]
      }
      chart.setOption(option)
    }

    // 修改用时分布图表初始化
    const initTimeDistChart = (data: any) => {
      if (!timeDistChart.value) return
      
      const chart = echarts.init(timeDistChart.value)
      const option: EChartsOption = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['简单题', '中等题', '困难题'],
          top: 10
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: ['0-3秒', '3-5秒', '5-10秒', '10-15秒', '15秒以上'],
          axisLabel: {
            interval: 0,
            rotate: 0,
            formatter: function (value: string) {
              return value.split('-').join('\n');
            },
            margin: 15,
            textStyle: {
              fontSize: 12,
              align: 'center'
            }
          },
          axisTick: {
            alignWithLabel: true
          }
        },
        yAxis: {
          type: 'value',
          name: '题目数量',
          nameGap: 15
        },
        series: [
          {
            name: '简单题',
            type: 'bar',
            stack: 'total',
            emphasis: {
              focus: 'series'
            },
            data: data.simple,
            itemStyle: {
              color: '#91cc75'  // 绿色
            },
            barWidth: '60%'
          },
          {
            name: '中等题',
            type: 'bar',
            stack: 'total',
            emphasis: {
              focus: 'series'
            },
            data: data.medium,
            itemStyle: {
              color: '#fac858'  // 黄色
            }
          },
          {
            name: '困难题',
            type: 'bar',
            stack: 'total',
            emphasis: {
              focus: 'series'
            },
            data: data.hard,
            itemStyle: {
              color: '#ee6666'  // 红色
            }
          }
        ]
      }
      chart.setOption(option)
    }

    // 格式化练习时间
    const formatPracticeTime = (minutes: number) => {
      if (minutes < 60) {
        return `${minutes}分钟`
      }
      const hours = Math.floor(minutes / 60)
      const remainingMinutes = minutes % 60
      return remainingMinutes > 0 ? 
        `${hours}小时${remainingMinutes}分钟` : 
        `${hours}小时`
    }

    onMounted(async () => {
      await fetchUserStats()
      
      // 监听窗口大小变化，重绘图表
      window.addEventListener('resize', () => {
        accuracyChart.value && echarts.getInstanceByDom(accuracyChart.value)?.resize()
        practiceCountChart.value && echarts.getInstanceByDom(practiceCountChart.value)?.resize()
        operatorChart.value && echarts.getInstanceByDom(operatorChart.value)?.resize()
        timeDistChart.value && echarts.getInstanceByDom(timeDistChart.value)?.resize()
      })
    })

    return {
      greeting,
      userName,
      userGrade,
      totalPractices,
      averageAccuracy,
      totalTime,
      trendTimeRange,
      accuracyChart,
      operatorChart,
      timeDistChart,
      practiceCountChart,
      isUpdating,
      refreshData,
      Refresh
    }
  }
})
</script>

<style scoped>
.home-container {
  padding: 20px;
  min-height: calc(100vh - 60px);
  background-color: #f5f7fa;
}

.welcome-card {
  height: calc(100vh - 100px);
}

.welcome-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.user-info {
  text-align: center;
  padding: 20px 0;
}

.user-info h3 {
  margin: 10px 0;
  font-size: 20px;
  color: #303133;
}

.grade {
  display: inline-block;
  padding: 4px 12px;
  background-color: #ecf5ff;
  color: #409EFF;
  border-radius: 16px;
  font-size: 14px;
}

.statistics-list {
  margin-top: 30px;
}

.stat-item {
  padding: 20px;
  margin-bottom: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
}

.stat-label {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.stat-value.total { color: #409EFF; }
.stat-value.accuracy { color: #67C23A; }
.stat-value.time { color: #E6A23C; }

.chart-card {
  margin-bottom: 20px;
  height: 480px;
  position: relative; /* 添加相对定位 */
}

.chart-container {
  height: calc(100% - 60px);
  width: 100%;
  padding: 10px;
  min-height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

/* 确保图表容器有足够的空间 */
.el-card {
  display: flex;
  flex-direction: column;
}

.el-card__body {
  flex: 1;
  padding: 10px;
}

/* 添加加载状态样式 */
:deep(.el-loading-mask) {
  z-index: 1000;
}

:deep(.el-loading-text) {
  font-size: 16px;
  margin-top: 10px;
}
</style> 