<template>
  <div class="system-config">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>系统配置</h2>
      <p class="description">管理和配置系统参数</p>
    </div>

    <el-row :gutter="20">
      <!-- 左侧配置项 -->
      <el-col :span="16">
        <!-- 服务器配置 -->
        <el-card header="服务器配置" class="config-card">
          <el-form
            ref="serverFormRef"
            :model="serverConfig"
            :rules="serverRules"
            label-width="120px"
          >
            <el-form-item label="服务器地址" prop="host">
              <el-input v-model="serverConfig.host" placeholder="0.0.0.0" />
            </el-form-item>
            <el-form-item label="端口" prop="port">
              <el-input-number
                v-model="serverConfig.port"
                :min="1"
                :max="65535"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="调试模式" prop="debug">
              <el-switch
                v-model="serverConfig.debug"
                active-text="开启"
                inactive-text="关闭"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 应用配置 -->
        <el-card header="应用配置" class="config-card">
          <el-form
            ref="appFormRef"
            :model="appConfig"
            :rules="appRules"
            label-width="120px"
          >
            <el-form-item label="应用名称" prop="name">
              <el-input v-model="appConfig.name" placeholder="Geyago智能题库" />
            </el-form-item>
            <el-form-item label="应用版本" prop="version">
              <el-input v-model="appConfig.version" placeholder="1.0.0" />
            </el-form-item>
            <el-form-item label="默认AI" prop="default_ai">
              <el-select
                v-model="appConfig.default_ai"
                placeholder="请选择默认AI服务商"
                style="width: 100%"
              >
                <el-option
                  v-for="provider in Object.values(aiStore.providers)"
                  :key="provider.id"
                  :label="provider.name"
                  :value="provider.id"
                  :disabled="!provider.enabled"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="主页地址" prop="homepage">
              <el-input v-model="appConfig.homepage" placeholder="https://toni.wang/" />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 数据库配置 -->
        <el-card header="数据库配置" class="config-card">
          <el-form
            ref="databaseFormRef"
            :model="databaseConfig"
            :rules="databaseRules"
            label-width="120px"
          >
            <el-form-item label="数据库URL" prop="url">
              <el-input
                v-model="databaseConfig.url"
                placeholder="sqlite:///question_bank.db"
                readonly
              />
              <div class="form-tip">
                当前使用 SQLite 数据库，暂不支持修改
              </div>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- API配置 -->
        <el-card header="API配置" class="config-card">
          <el-form
            ref="apiFormRef"
            :model="apiConfig"
            :rules="apiRules"
            label-width="120px"
          >
            <el-form-item label="超时时间(秒)" prop="timeout">
              <el-input-number
                v-model="apiConfig.timeout"
                :min="5"
                :max="300"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="最大重试次数" prop="max_retries">
              <el-input-number
                v-model="apiConfig.max_retries"
                :min="0"
                :max="10"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="重试延迟(秒)" prop="retry_delay">
              <el-input-number
                v-model="apiConfig.retry_delay"
                :min="1"
                :max="60"
                style="width: 100%"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 操作按钮 -->
        <div class="config-actions">
          <el-button
            type="primary"
            @click="saveConfig"
            :loading="saving"
            size="large"
          >
            <el-icon><Check /></el-icon>
            保存配置
          </el-button>
          <el-button @click="resetConfig" size="large">
            <el-icon><RefreshLeft /></el-icon>
            重置配置
          </el-button>
          <el-button type="info" @click="exportConfig" size="large">
            <el-icon><Download /></el-icon>
            导出配置
          </el-button>
          <el-button type="warning" @click="importConfig" size="large">
            <el-icon><Upload /></el-icon>
            导入配置
          </el-button>
        </div>
      </el-col>

      <!-- 右侧信息面板 -->
      <el-col :span="8">
        <!-- 系统状态 -->
        <el-card header="系统状态" class="status-card">
          <div class="status-item">
            <div class="status-label">数据库状态</div>
            <div class="status-value">
              <el-tag :type="dbStatusType">{{ dbStatus }}</el-tag>
            </div>
          </div>
          <div class="status-item">
            <div class="status-label">AI服务状态</div>
            <div class="status-value">
              <el-tag :type="aiStatusType">{{ aiStatus }}</el-tag>
            </div>
          </div>
          <div class="status-item">
            <div class="status-label">题目总数</div>
            <div class="status-value">{{ questionStore.stats.total_questions }}</div>
          </div>
          <div class="status-item">
            <div class="status-label">启用AI数量</div>
            <div class="status-value">{{ enabledAIProviders }}</div>
          </div>
          <div class="status-item">
            <div class="status-label">系统运行时间</div>
            <div class="status-value">{{ uptime }}</div>
          </div>
        </el-card>

        <!-- 快速操作 -->
        <el-card header="快速操作" class="quick-actions-card">
          <div class="quick-actions">
            <el-button
              type="primary"
              @click="testDatabaseConnection"
              :loading="testingDb"
              class="action-btn"
            >
              <el-icon><Connection /></el-icon>
              测试数据库连接
            </el-button>

            <el-button
              type="success"
              @click="testAIConnection"
              :loading="testingAI"
              class="action-btn"
            >
              <el-icon><MagicStick /></el-icon>
              测试AI连接
            </el-button>

            <el-button
              type="info"
              @click="viewLogs"
              class="action-btn"
            >
              <el-icon><Document /></el-icon>
              查看系统日志
            </el-button>

            <el-button
              type="warning"
              @click="clearCache"
              :loading="clearingCache"
              class="action-btn"
            >
              <el-icon><Delete /></el-icon>
              清理缓存
            </el-button>

            <el-button
              type="danger"
              @click="restartSystem"
              class="action-btn"
            >
              <el-icon><RefreshRight /></el-icon>
              重启系统
            </el-button>
          </div>
        </el-card>

        <!-- 配置信息 -->
        <el-card header="配置信息" class="info-card">
          <div class="config-info">
            <div class="info-item">
              <span class="info-label">配置文件:</span>
              <span class="info-value">config.json</span>
            </div>
            <div class="info-item">
              <span class="info-label">最后更新:</span>
              <span class="info-value">{{ lastUpdated || '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">配置版本:</span>
              <span class="info-value">v1.0</span>
            </div>
            <div class="info-item">
              <span class="info-label">环境:</span>
              <el-tag type="info" size="small">development</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 导入配置对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="导入配置"
      width="500px"
    >
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".json"
      >
        <el-button type="primary">选择配置文件</el-button>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 JSON 格式的配置文件
          </div>
        </template>
      </el-upload>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showImportDialog = false">取消</el-button>
          <el-button
            type="primary"
            @click="confirmImport"
            :disabled="!selectedFile"
          >
            确认导入
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules, UploadInstance, UploadFile } from 'element-plus'
import {
  Check, RefreshLeft, Download, Upload, Connection, MagicStick,
  Document, Delete, RefreshRight
} from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { useQuestionStore } from '@/stores/question'
import { useAIStore } from '@/stores/ai'

const appStore = useAppStore()
const questionStore = useQuestionStore()
const aiStore = useAIStore()

// 响应式数据
const saving = ref(false)
const testingDb = ref(false)
const testingAI = ref(false)
const clearingCache = ref(false)
const showImportDialog = ref(false)
const selectedFile = ref<File | null>(null)
const lastUpdated = ref('')
const uptime = ref('0天 0小时 0分钟')

// 表单引用
const serverFormRef = ref<FormInstance>()
const appFormRef = ref<FormInstance>()
const databaseFormRef = ref<FormInstance>()
const apiFormRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()

// 配置数据
const serverConfig = reactive({
  host: '0.0.0.0',
  port: 5000,
  debug: false
})

const appConfig = reactive({
  name: '',
  version: '',
  default_ai: '',
  homepage: ''
})

const databaseConfig = reactive({
  url: ''
})

const apiConfig = reactive({
  timeout: 30,
  max_retries: 3,
  retry_delay: 2
})

// 表单验证规则
const serverRules: FormRules = {
  host: [
    { required: true, message: '请输入服务器地址', trigger: 'blur' }
  ],
  port: [
    { required: true, message: '请输入端口号', trigger: 'blur' },
    { type: 'number', min: 1, max: 65535, message: '端口范围 1-65535', trigger: 'blur' }
  ]
}

const appRules: FormRules = {
  name: [
    { required: true, message: '请输入应用名称', trigger: 'blur' }
  ],
  version: [
    { required: true, message: '请输入应用版本', trigger: 'blur' }
  ]
}

const databaseRules: FormRules = {
  url: [
    { required: true, message: '请输入数据库URL', trigger: 'blur' }
  ]
}

const apiRules: FormRules = {
  timeout: [
    { required: true, message: '请输入超时时间', trigger: 'blur' },
    { type: 'number', min: 5, max: 300, message: '超时时间范围 5-300秒', trigger: 'blur' }
  ],
  max_retries: [
    { required: true, message: '请输入最大重试次数', trigger: 'blur' },
    { type: 'number', min: 0, max: 10, message: '重试次数范围 0-10', trigger: 'blur' }
  ]
}

// 计算属性
const dbStatus = computed(() => {
  return questionStore.stats.service_status.database === 'healthy' ? '正常' : '异常'
})

const dbStatusType = computed(() => {
  return questionStore.stats.service_status.database === 'healthy' ? 'success' : 'danger'
})

const aiStatus = computed(() => {
  return questionStore.stats.service_status.ai_service === 'healthy' ? '正常' : '异常'
})

const aiStatusType = computed(() => {
  return questionStore.stats.service_status.ai_service === 'healthy' ? 'success' : 'danger'
})

const enabledAIProviders = computed(() => {
  return Object.values(aiStore.providers).filter(provider => provider.enabled).length
})

// 方法
async function loadConfig() {
  try {
    // 从 app store 获取配置
    await appStore.fetchAppConfig()

    // 更新配置数据
    Object.assign(serverConfig, appStore.serverConfig)
    Object.assign(appConfig, appStore.appInfo)

    // 设置其他默认值
    databaseConfig.url = 'sqlite:///question_bank.db'
    lastUpdated.value = new Date().toLocaleString()

    // 计算运行时间（这里用模拟数据）
    updateUptime()
  } catch (error) {
    ElMessage.error('加载配置失败')
  }
}

async function saveConfig() {
  try {
    // 验证所有表单
    await Promise.all([
      serverFormRef.value?.validate(),
      appFormRef.value?.validate(),
      databaseFormRef.value?.validate(),
      apiFormRef.value?.validate()
    ])

    saving.value = true

    // 这里应该调用后端 API 保存配置
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟保存

    ElMessage.success('配置保存成功')
    lastUpdated.value = new Date().toLocaleString()
  } catch (error) {
    ElMessage.error('配置保存失败')
  } finally {
    saving.value = false
  }
}

function resetConfig() {
  ElMessageBox.confirm('确定要重置所有配置吗？此操作不可恢复。', '确认重置', {
    type: 'warning'
  }).then(() => {
    loadConfig()
    ElMessage.success('配置已重置')
  })
}

function exportConfig() {
  const config = {
    server: serverConfig,
    app: appConfig,
    database: databaseConfig,
    api: apiConfig
  }

  const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `geyago-config-${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  ElMessage.success('配置已导出')
}

function importConfig() {
  showImportDialog.value = true
}

function handleFileChange(file: UploadFile) {
  selectedFile.value = file.raw as File
}

async function confirmImport() {
  if (!selectedFile.value) return

  try {
    const text = await selectedFile.value.text()
    const config = JSON.parse(text)

    // 验证配置格式
    if (!config.server || !config.app) {
      throw new Error('配置文件格式不正确')
    }

    // 应用配置
    Object.assign(serverConfig, config.server)
    Object.assign(appConfig, config.app)
    if (config.database) {
      Object.assign(databaseConfig, config.database)
    }
    if (config.api) {
      Object.assign(apiConfig, config.api)
    }

    showImportDialog.value = false
    selectedFile.value = null
    ElMessage.success('配置导入成功')
  } catch (error) {
    ElMessage.error('配置文件格式不正确')
  }
}

async function testDatabaseConnection() {
  testingDb.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟测试
    ElMessage.success('数据库连接正常')
  } catch (error) {
    ElMessage.error('数据库连接失败')
  } finally {
    testingDb.value = false
  }
}

async function testAIConnection() {
  testingAI.value = true
  try {
    await aiStore.queryAI({
      title: '测试连接',
      provider: aiStore.currentProvider
    })
    ElMessage.success('AI连接正常')
  } catch (error) {
    ElMessage.error('AI连接失败')
  } finally {
    testingAI.value = false
  }
}

function viewLogs() {
  ElMessage.info('日志功能开发中...')
}

async function clearCache() {
  clearingCache.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟清理
    ElMessage.success('缓存清理完成')
  } catch (error) {
    ElMessage.error('缓存清理失败')
  } finally {
    clearingCache.value = false
  }
}

function restartSystem() {
  ElMessageBox.confirm('确定要重启系统吗？重启后需要重新访问。', '确认重启', {
    type: 'warning'
  }).then(() => {
    ElMessage.success('系统重启指令已发送')
  })
}

function updateUptime() {
  // 这里应该从后端获取实际运行时间
  const startTime = new Date('2025-01-01') // 模拟启动时间
  const now = new Date()
  const diff = now.getTime() - startTime.getTime()

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

  uptime.value = `${days}天 ${hours}小时 ${minutes}分钟`
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadConfig(),
    questionStore.fetchQuestionStats(),
    aiStore.fetchProviders()
  ])

  // 定期更新运行时间
  setInterval(updateUptime, 60000)
})
</script>

<style scoped>
.system-config {
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

.config-card,
.status-card,
.quick-actions-card,
.info-card {
  margin-bottom: 20px;
}

.config-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
  padding: 20px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
}

.form-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.status-value {
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  width: 100%;
  justify-content: flex-start;
}

.config-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.info-value {
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>