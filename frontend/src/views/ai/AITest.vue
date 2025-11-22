<template>
  <div class="ai-test">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>AI 服务测试</h2>
      <p class="description">测试不同 AI 服务商的问答效果</p>
    </div>

    <el-row :gutter="20">
      <!-- 左侧测试表单 -->
      <el-col :span="16">
        <el-card header="测试配置" class="test-config-card">
          <el-form
            ref="testFormRef"
            :model="testForm"
            :rules="testFormRules"
            label-width="100px"
          >
            <el-form-item label="AI 服务商" prop="provider">
              <el-select
                v-model="testForm.provider"
                placeholder="请选择 AI 服务商"
                style="width: 100%"
                @change="onProviderChange"
                :disabled="loading"
              >
                <el-option
                  v-for="provider in enabledProviders"
                  :key="provider.id"
                  :label="provider.name"
                  :value="provider.id"
                >
                  <div class="provider-option">
                    <span>{{ provider.name }}</span>
                    <el-tag v-if="aiStore.currentProvider === provider.id" type="primary" size="small">
                      默认
                    </el-tag>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="模型" prop="model">
              <el-select
                v-model="testForm.model"
                placeholder="请选择模型"
                style="width: 100%"
                :disabled="!testForm.provider || loading"
                :loading="modelsLoading"
              >
                <el-option
                  v-for="model in currentModels"
                  :key="model"
                  :label="model"
                  :value="model"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="问题类型" prop="type">
              <el-select
                v-model="testForm.type"
                placeholder="请选择问题类型"
                style="width: 100%"
              >
                <el-option label="单选题" value="single" />
                <el-option label="多选题" value="multiple" />
                <el-option label="判断题" value="judgement" />
                <el-option label="填空题" value="fill" />
                <el-option label="简答题" value="essay" />
              </el-select>
            </el-form-item>

            <el-form-item label="问题内容" prop="question">
              <el-input
                v-model="testForm.question"
                type="textarea"
                :rows="3"
                placeholder="请输入测试问题"
                maxlength="1000"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="选项" prop="options">
              <el-input
                v-model="testForm.options"
                type="textarea"
                :rows="2"
                placeholder="请输入选项（单选题/多选题需要），例如：A.1 B.2 C.3 D.4"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="runTest"
                :loading="loading"
                :disabled="!testForm.provider || !testForm.question"
              >
                <el-icon><Cpu /></el-icon>
                开始测试
              </el-button>
              <el-button @click="clearForm">
                <el-icon><Delete /></el-icon>
                清空表单
              </el-button>
              <el-button type="info" @click="loadExample">
                <el-icon><Document /></el-icon>
                加载示例
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧快速模板 -->
      <el-col :span="8">
        <el-card header="测试模板" class="templates-card">
          <div class="template-list">
            <div
              v-for="template in testTemplates"
              :key="template.name"
              class="template-item"
              @click="applyTemplate(template)"
            >
              <div class="template-name">{{ template.name }}</div>
              <div class="template-desc">{{ template.description }}</div>
            </div>
          </div>
        </el-card>

        <!-- 测试历史 -->
        <el-card header="测试历史" class="history-card">
          <div v-if="testHistory.length === 0" class="empty-history">
            <el-empty description="暂无测试历史" :image-size="80" />
          </div>
          <div v-else class="history-list">
            <div
              v-for="(item, index) in testHistory"
              :key="index"
              class="history-item"
              @click="applyHistory(item)"
            >
              <div class="history-question">{{ item.question.slice(0, 50) }}...</div>
              <div class="history-meta">
                <span class="provider">{{ item.provider }}</span>
                <span class="time">{{ formatTime(item.time) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 测试结果 -->
    <el-row v-if="testResult" class="result-row">
      <el-col :span="24">
        <el-card header="测试结果" class="result-card">
          <div class="result-content">
            <!-- 结果概览 -->
            <el-descriptions :column="4" border class="result-overview">
              <el-descriptions-item label="服务商">
                <el-tag type="primary">{{ testResult.provider }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="模型">
                <el-tag>{{ testResult.model }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="状态码">
                <el-tag :type="testResult.code === 0 ? 'success' : 'warning'">
                  {{ testResult.code }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="数据来源">
                <el-tag :type="getSourceType(testResult.source)">
                  {{ getSourceLabel(testResult.source) }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>

            <!-- 详细信息 -->
            <div class="result-details">
              <div class="detail-section">
                <h4>问题描述</h4>
                <el-input
                  v-model="testForm.question"
                  type="textarea"
                  :rows="2"
                  readonly
                />
              </div>

              <div v-if="testForm.options" class="detail-section">
                <h4>选项</h4>
                <el-input
                  v-model="testForm.options"
                  type="textarea"
                  :rows="1"
                  readonly
                />
              </div>

              <div class="detail-section">
                <h4>AI 回答</h4>
                <el-input
                  v-model="testResult.data"
                  type="textarea"
                  :rows="4"
                  readonly
                  class="answer-input"
                />
              </div>

              <div class="detail-section">
                <h4>响应消息</h4>
                <p class="response-message">{{ testResult.msg }}</p>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="result-actions">
              <el-button
                type="primary"
                @click="copyResult"
              >
                <el-icon><CopyDocument /></el-icon>
                复制结果
              </el-button>
              <el-button
                type="success"
                @click="saveToDatabase"
                :disabled="!testResult.data || testResult.source === 'database'"
              >
                <el-icon><Plus /></el-icon>
                保存到题库
              </el-button>
              <el-button
                type="info"
                @click="testAgain"
              >
                <el-icon><Refresh /></el-icon>
                重新测试
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Cpu, Delete, Document, CopyDocument, Plus, Refresh
} from '@element-plus/icons-vue'
import { useAIStore } from '@/stores/ai'
import type { AIQueryResult } from '@/stores/ai'
import type { FormInstance, FormRules } from 'element-plus'

const aiStore = useAIStore()

// 响应式数据
const loading = ref(false)
const modelsLoading = ref(false)
const testFormRef = ref<FormInstance>()
const currentModels = ref<string[]>([])
const testResult = ref<AIQueryResult | null>(null)
const testHistory = ref<any[]>([])

// 表单数据
const testForm = reactive({
  provider: '',
  model: '',
  type: 'single',
  question: '',
  options: ''
})

// 表单规则
const testFormRules: FormRules = {
  provider: [
    { required: true, message: '请选择 AI 服务商', trigger: 'change' }
  ],
  question: [
    { required: true, message: '请输入测试问题', trigger: 'blur' }
  ]
}

// 测试模板
const testTemplates = [
  {
    name: '数学计算',
    description: '1+1 等于多少？',
    type: 'single',
    question: '1+1 等于多少？',
    options: 'A.1 B.2 C.3 D.4'
  },
  {
    name: '历史知识',
    description: '中国的首都是哪里？',
    type: 'single',
    question: '中国的首都是哪里？',
    options: 'A.上海 B.北京 C.广州 D.深圳'
  },
  {
    name: '科学概念',
    description: '水的化学式是什么？',
    type: 'single',
    question: '水的化学式是什么？',
    options: 'A.H2O B.CO2 C.O2 D.N2'
  },
  {
    name: '编程问题',
    description: 'Python 中如何定义列表？',
    type: 'essay',
    question: 'Python 中如何定义列表？请给出示例代码。',
    options: ''
  }
]

// 计算属性
const enabledProviders = computed(() => {
  return Object.entries(aiStore.providers)
    .filter(([key, provider]) => provider.enabled)
    .map(([key, provider]) => ({
      ...provider,
      id: key  // 将对象键作为ID
    }))
})

// 方法
async function onProviderChange() {
  if (!testForm.provider) {
    currentModels.value = []
    testForm.model = ''
    return
  }

  try {
    modelsLoading.value = true
    const models = await aiStore.getProviderModels(testForm.provider)
    currentModels.value = models || []

    // 设置默认模型
    const provider = aiStore.providers[testForm.provider]
    if (provider && models.includes(provider.models.default)) {
      testForm.model = provider.models.default
    } else if (models.length > 0) {
      testForm.model = models[0]
    }
  } catch (error) {
    ElMessage.error('获取模型列表失败')
  } finally {
    modelsLoading.value = false
  }
}

async function runTest() {
  if (!testFormRef.value) return

  try {
    await testFormRef.value.validate()

    loading.value = true
    testResult.value = null

    const result = await aiStore.queryAI({
      title: testForm.question,
      options: testForm.options,
      provider: testForm.provider,
      model: testForm.model
    })

    testResult.value = {
      ...result,
      provider: aiStore.providers[testForm.provider]?.name,
      model: testForm.model
    }

    // 添加到历史记录
    addToHistory()

    ElMessage.success('测试完成')
  } catch (error) {
    ElMessage.error('测试失败')
  } finally {
    loading.value = false
  }
}

function clearForm() {
  testForm.provider = ''
  testForm.model = ''
  testForm.type = 'single'
  testForm.question = ''
  testForm.options = ''
  currentModels.value = []
  testResult.value = null
}

function loadExample() {
  const template = testTemplates[Math.floor(Math.random() * testTemplates.length)]
  applyTemplate(template)
}

function applyTemplate(template: any) {
  testForm.type = template.type
  testForm.question = template.question
  testForm.options = template.options
}

function addToHistory() {
  if (!testForm.question) return

  testHistory.value.unshift({
    question: testForm.question,
    options: testForm.options,
    provider: aiStore.providers[testForm.provider]?.name,
    providerId: testForm.provider,
    model: testForm.model,
    type: testForm.type,
    time: new Date().toISOString()
  })

  // 最多保留 10 条历史记录
  if (testHistory.value.length > 10) {
    testHistory.value = testHistory.value.slice(0, 10)
  }
}

function applyHistory(item: any) {
  testForm.provider = item.providerId || item.provider  // 兼容旧数据格式
  testForm.model = item.model
  testForm.type = item.type
  testForm.question = item.question
  testForm.options = item.options
  onProviderChange()
}

function formatTime(timeString: string) {
  return new Date(timeString).toLocaleString()
}

function getSourceType(source: string | null) {
  switch (source) {
    case 'database':
      return 'success'
    case 'ai':
      return 'primary'
    default:
      return 'warning'
  }
}

function getSourceLabel(source: string | null) {
  switch (source) {
    case 'database':
      return '数据库'
    case 'ai':
      return 'AI 生成'
    default:
      return '未知来源'
  }
}

function copyResult() {
  if (!testResult.value) return

  const text = `问题: ${testForm.question}\n${testForm.options ? `选项: ${testForm.options}\n` : ''}回答: ${testResult.value.data}`

  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

async function saveToDatabase() {
  if (!testResult.value || !testResult.value.data) return

  try {
    await ElMessageBox.confirm('确定要将此问答保存到题库吗？', '确认保存', {
      type: 'warning'
    })

    // 这里需要调用保存到题库的 API
    ElMessage.success('保存成功')
  } catch {
    // 用户取消
  }
}

function testAgain() {
  runTest()
}

// 生命周期
onMounted(() => {
  aiStore.fetchProviders()
})
</script>

<style scoped>
.ai-test {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: var(--el-text-color-primary);
}

.description {
  margin: 0;
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.test-config-card,
.templates-card,
.history-card {
  margin-bottom: 20px;
}

.provider-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.template-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.template-item {
  padding: 12px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.template-item:hover {
  background-color: var(--el-bg-color-page);
  border-color: var(--el-color-primary);
}

.template-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.template-desc {
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.empty-history {
  padding: 20px;
  text-align: center;
}

.history-list {
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  padding: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  cursor: pointer;
  transition: background-color 0.3s;
}

.history-item:hover {
  background-color: var(--el-bg-color-page);
}

.history-item:last-child {
  border-bottom: none;
}

.history-question {
  font-size: 14px;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.history-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.history-meta .provider {
  color: var(--el-color-primary);
}

.history-meta .time {
  color: var(--el-text-color-secondary);
}

.result-row {
  margin-top: 20px;
}

.result-card {
  margin-bottom: 20px;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-overview {
  margin-bottom: 20px;
}

.result-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-section h4 {
  margin: 0 0 8px 0;
  color: var(--el-text-color-primary);
  font-size: 14px;
}

.answer-input {
  font-family: monospace;
}

.response-message {
  background-color: var(--el-bg-color-page);
  padding: 12px;
  border-radius: 8px;
  margin: 0;
  color: var(--el-text-color-regular);
  border-left: 4px solid var(--el-color-primary);
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}
</style>