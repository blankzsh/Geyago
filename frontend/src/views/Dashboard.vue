<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon questions">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-number">{{ questionStore.stats.total_questions }}</div>
              <div class="stats-label">题目总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon providers">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-number">{{ enabledProvidersCount }}</div>
              <div class="stats-label">可用AI服务商</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon database">
              <el-icon><Coin /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-number">{{ dbStatus }}</div>
              <div class="stats-label">数据库状态</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon ai">
              <el-icon><MagicStick /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-number">{{ aiStatus }}</div>
              <div class="stats-label">AI服务状态</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表和快速操作 -->
    <el-row :gutter="20" class="content-row">
      <!-- 左侧图表 -->
      <el-col :span="16">
        <el-card header="系统概览" class="chart-card">
          <div class="chart-container">
            <v-chart :option="chartOption" style="height: 300px;" />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧快速操作 -->
      <el-col :span="8">
        <el-card header="快速操作" class="quick-actions-card">
          <div class="quick-actions">
            <el-button
              type="primary"
              size="large"
              @click="$router.push('/questions/add')"
              class="action-btn"
            >
              <el-icon><Plus /></el-icon>
              添加题目
            </el-button>

            <el-button
              type="success"
              size="large"
              @click="$router.push('/ai/test')"
              class="action-btn"
            >
              <el-icon><Cpu /></el-icon>
              测试AI
            </el-button>

            <el-button
              type="info"
              size="large"
              @click="$router.push('/questions/list')"
              class="action-btn"
            >
              <el-icon><List /></el-icon>
              题目列表
            </el-button>

            <el-button
              type="warning"
              size="large"
              @click="$router.push('/ai/providers')"
              class="action-btn"
            >
              <el-icon><Setting /></el-icon>
              AI配置
            </el-button>
          </div>
        </el-card>

        <!-- 系统信息 -->
        <el-card header="系统信息" class="system-info-card">
          <div class="system-info">
            <div class="info-item">
              <span class="info-label">应用名称:</span>
              <span class="info-value">{{ appStore.appInfo?.name || 'Geyago智能题库' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">版本:</span>
              <span class="info-value">{{ appStore.appInfo?.version || '1.0.0' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">服务器:</span>
              <span class="info-value">{{ serverAddress }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">调试模式:</span>
              <el-tag :type="appStore.serverConfig?.debug ? 'warning' : 'success'" size="small">
                {{ appStore.serverConfig?.debug ? '开启' : '关闭' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近添加的题目 -->
    <el-row :gutter="20" class="recent-questions-row">
      <el-col :span="24">
        <el-card header="最近添加的题目" class="recent-questions-card">
          <el-table
            :data="recentQuestions"
            stripe
            style="width: 100%"
            v-loading="questionStore.loading"
          >
            <el-table-column prop="question_text" label="问题" show-overflow-tooltip />
            <el-table-column prop="answer" label="答案" show-overflow-tooltip />
            <el-table-column prop="question_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ getQuestionTypeLabel(row.question_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button
                  text
                  type="primary"
                  size="small"
                  @click="viewQuestion(row)"
                >
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="table-footer">
            <el-button
              text
              type="primary"
              @click="$router.push('/questions/list')"
            >
              查看全部题目 →
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import {
  Document, Connection, Coin, MagicStick, Plus, Cpu,
  List, Setting, Check, Close, InfoFilled
} from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { useQuestionStore } from '@/stores/question'
import { useAIStore } from '@/stores/ai'

// 注册 ECharts 组件
use([CanvasRenderer, PieChart, TitleComponent, TooltipComponent, LegendComponent])

const appStore = useAppStore()
const questionStore = useQuestionStore()
const aiStore = useAIStore()

const recentQuestions = ref([])

// 计算属性
const enabledProvidersCount = computed(() => {
  return Object.values(aiStore.providers).filter(provider => provider.enabled).length
})

const dbStatus = computed(() => {
  return questionStore.stats.service_status.database === 'healthy' ? '正常' : '异常'
})

const aiStatus = computed(() => {
  return questionStore.stats.service_status.ai_service === 'healthy' ? '正常' : '异常'
})

const serverAddress = computed(() => {
  return `${appStore.serverConfig?.host || '0.0.0.0'}:${appStore.serverConfig?.port || 5000}`
})

const chartOption = computed(() => ({
  title: {
    text: 'AI 服务商分布',
    left: 'center'
  },
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: 'AI 服务商',
      type: 'pie',
      radius: '50%',
      data: Object.values(aiStore.providers).map(provider => ({
        value: provider.enabled ? 1 : 0,
        name: provider.name
      })),
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
}))

// 方法
function getQuestionTypeLabel(type?: string) {
  const typeMap: Record<string, string> = {
    single: '单选',
    multiple: '多选',
    judgement: '判断',
    fill: '填空',
    essay: '简答'
  }
  return typeMap[type || 'unknown'] || '未知'
}

function formatDateTime(dateString?: string) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString()
}

function viewQuestion(question: any) {
  // 跳转到题目详情页
  // 这里可以实现查看题目的逻辑
  console.log('查看题目:', question)
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    appStore.fetchAppConfig(),
    appStore.fetchSystemStats(),
    questionStore.fetchQuestionStats(),
    aiStore.fetchProviders(),
    questionStore.fetchQuestions(1, '', 5) // 获取最近5条数据
  ])

  recentQuestions.value = questionStore.questions.slice(0, 5)
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stats-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.stats-content {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 24px;
  color: white;
}

.stats-icon.questions {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-icon.providers {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stats-icon.database {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stats-icon.ai {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stats-info {
  flex: 1;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: var(--el-text-color-primary);
  line-height: 1;
}

.stats-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
  margin-top: 4px;
}

.content-row {
  margin-bottom: 20px;
}

.chart-card,
.quick-actions-card,
.system-info-card {
  margin-bottom: 20px;
}

.chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-btn {
  width: 100%;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 16px;
}

.system-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.info-label {
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.info-value {
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.recent-questions-row {
  margin-bottom: 20px;
}

.table-footer {
  display: flex;
  justify-content: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}
</style>