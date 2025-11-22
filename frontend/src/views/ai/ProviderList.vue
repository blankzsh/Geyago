<template>
  <div class="provider-list">
    <!-- 页面标题和操作 -->
    <div class="page-header">
      <div class="header-left">
        <h2>AI 服务商管理</h2>
        <p class="description">管理和配置不同的 AI 服务提供商</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="refreshProviders">
          <el-icon><Refresh /></el-icon>
          刷新列表
        </el-button>
      </div>
    </div>

    <!-- 服务商列表 -->
    <el-row :gutter="20">
      <el-col :span="8" v-for="provider in Object.values(aiStore.providers)" :key="provider.id">
        <el-card class="provider-card" :class="{
          'enabled': provider.enabled,
          'is-default': aiStore.currentProvider === provider.id
        }">
          <template #header>
            <div class="card-header">
              <div class="provider-info">
                <div class="provider-name">
                  <h3>{{ provider.name }}</h3>
                  <el-tag v-if="aiStore.currentProvider === provider.id" type="warning" size="small">
                    默认
                  </el-tag>
                </div>
                <el-tag :type="provider.enabled ? 'success' : 'info'" size="small">
                  {{ provider.enabled ? '已启用' : '未启用' }}
                </el-tag>
              </div>
              <div class="provider-actions">
                <el-switch
                  v-model="provider.enabled"
                  @change="toggleProvider(provider.id, $event)"
                  :loading="loadingProviders.includes(provider.id)"
                />
              </div>
            </div>
          </template>

          <div class="provider-content">
            <!-- 服务商信息 -->
            <div class="provider-details">
              <div class="detail-item">
                <span class="label">API 地址:</span>
                <span class="value">{{ provider.base_url }}</span>
              </div>
              <div class="detail-item">
                <span class="label">默认模型:</span>
                <span class="value">{{ provider.models.default }}</span>
              </div>
              <div class="detail-item">
                <span class="label">可用模型:</span>
                <span class="value">{{ provider.models.available.length }} 个</span>
              </div>
            </div>

            <!-- 模型列表 -->
            <div class="models-section">
              <h4>模型列表</h4>
              <el-scrollbar height="120px">
                <div class="model-list">
                  <el-tag
                    v-for="model in provider.models.available"
                    :key="model"
                    :type="model === provider.models.default ? 'primary' : ''"
                    size="small"
                    class="model-tag"
                  >
                    {{ model }}
                  </el-tag>
                </div>
              </el-scrollbar>
            </div>

            <!-- 操作按钮 -->
            <div class="provider-actions-bottom">
              <el-button
                type="primary"
                size="small"
                @click="editProvider(provider)"
                :disabled="!provider.enabled"
              >
                <el-icon><Edit /></el-icon>
                配置
              </el-button>
              <el-button
                type="success"
                size="small"
                @click="openTestDialog(provider)"
                :disabled="!provider.enabled"
              >
                <el-icon><Cpu /></el-icon>
                测试
              </el-button>
              <el-dropdown @command="handleProviderAction">
                <el-button type="info" size="small" text>
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      :command="{ action: 'setDefault', provider }"
                      :disabled="!provider.enabled || aiStore.currentProvider === provider.id"
                    >
                      设为默认
                    </el-dropdown-item>
                    <el-dropdown-item
                      :command="{ action: 'viewModels', provider }"
                      :disabled="!provider.enabled"
                    >
                      查看模型详情
                    </el-dropdown-item>
                    <el-dropdown-item
                      :command="{ action: 'manageModels', provider }"
                      :disabled="!provider.enabled"
                    >
                      管理模型
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 编辑配置对话框 -->
    <el-dialog
      v-model="showEditDialog"
      :title="`配置 ${editingProvider?.name}`"
      width="600px"
    >
      <el-form
        v-if="editingProvider"
        ref="editFormRef"
        :model="editForm"
        :rules="editFormRules"
        label-width="100px"
      >
        <el-form-item label="API 密钥" prop="api_key">
          <el-input
            v-model="editForm.api_key"
            type="password"
            show-password
            placeholder="请输入 API 密钥"
          />
        </el-form-item>
        <el-form-item label="API 地址" prop="base_url">
          <el-input
            v-model="editForm.base_url"
            placeholder="请输入 API 地址"
          />
        </el-form-item>
        <el-form-item label="默认模型" prop="defaultModel">
          <el-select
            v-model="editForm.defaultModel"
            placeholder="请选择默认模型"
            style="width: 100%"
          >
            <el-option
              v-for="model in editingProvider.models.available"
              :key="model"
              :label="model"
              :value="model"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button
            type="primary"
            @click="saveProviderConfig"
            :loading="saving"
          >
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 测试对话框 -->
    <el-dialog
      v-model="showTestDialog"
      title="AI 服务测试"
      width="700px"
    >
      <div v-if="testProvider" class="test-content">
        <div class="test-info">
          <p>测试服务商: <strong>{{ testProvider.name }}</strong></p>
          <p>使用模型: <strong>{{ testProvider.models.default }}</strong></p>
        </div>

        <el-form @submit.prevent="runAITest">
          <el-form-item label="测试问题">
            <el-input
              v-model="testQuestion"
              placeholder="请输入测试问题，例如：1+1=?"
              @keyup.enter="runAITest"
            />
          </el-form-item>
          <el-form-item label="选项（可选）">
            <el-input
              v-model="testOptions"
              placeholder="请输入选项，例如：A.1 B.2 C.3"
            />
          </el-form-item>
        </el-form>

        <div class="test-actions">
          <el-button
            type="primary"
            @click="runAITest"
            :loading="aiStore.loading"
          >
            <el-icon><Cpu /></el-icon>
            开始测试
          </el-button>
        </div>

        <!-- 测试结果 -->
        <div v-if="aiStore.testResult" class="test-result">
          <el-divider>测试结果</el-divider>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="状态码">
              <el-tag :type="aiStore.testResult.code === 0 ? 'success' : 'warning'">
                {{ aiStore.testResult.code }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="消息">
              {{ aiStore.testResult.msg }}
            </el-descriptions-item>
            <el-descriptions-item label="数据来源">
              <el-tag :type="getSourceType(aiStore.testResult.source)">
                {{ getSourceLabel(aiStore.testResult.source) }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <div v-if="aiStore.testResult.data" class="answer-section">
            <h4>答案内容:</h4>
            <el-input
              v-model="aiStore.testResult.data"
              type="textarea"
              :rows="4"
              readonly
            />
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 模型管理对话框 -->
    <ModelManagementDialog
      v-model="showModelManagementDialog"
      :provider="modelManagementProvider"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Edit, Cpu, MoreFilled, Connection, Check, Close
} from '@element-plus/icons-vue'
import { useAIStore } from '@/stores/ai'
import type { AIProvider } from '@/stores/ai'
import type { FormInstance, FormRules } from 'element-plus'
import ModelManagementDialog from '@/components/ModelManagementDialog.vue'

const aiStore = useAIStore()

// 状态
const loadingProviders = ref<string[]>([])
const showEditDialog = ref(false)
const showTestDialog = ref(false)
const editingProvider = ref<AIProvider | null>(null)
const testProvider = ref<AIProvider | null>(null)
const testQuestion = ref('1+1等于多少？')
const testOptions = ref('A.1 B.2 C.3 D.4')
const saving = ref(false)
const editFormRef = ref<FormInstance>()
const showModelManagementDialog = ref(false)
const modelManagementProvider = ref<AIProvider | null>(null)

// 编辑表单
const editForm = reactive({
  api_key: '',
  base_url: '',
  defaultModel: ''
})

// 表单规则
const editFormRules: FormRules = {
  api_key: [
    { required: true, message: '请输入 API 密钥', trigger: 'blur' }
  ],
  base_url: [
    { required: true, message: '请输入 API 地址', trigger: 'blur' }
  ],
  defaultModel: [
    { required: true, message: '请选择默认模型', trigger: 'change' }
  ]
}

// 方法
async function refreshProviders() {
  try {
    await aiStore.fetchProviders()
    ElMessage.success('刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

async function toggleProvider(providerId: string, enabled: boolean) {
  loadingProviders.value.push(providerId)
  try {
    await aiStore.updateProviderConfig(providerId, { enabled })
    ElMessage.success(`${enabled ? '启用' : '禁用'}成功`)
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    loadingProviders.value = loadingProviders.value.filter(id => id !== providerId)
  }
}

function editProvider(provider: AIProvider) {
  editingProvider.value = provider
  editForm.api_key = ''
  editForm.base_url = provider.base_url
  editForm.defaultModel = provider.models.default
  showEditDialog.value = true
}

async function saveProviderConfig() {
  if (!editFormRef.value || !editingProvider.value) return

  try {
    await editFormRef.value.validate()
    saving.value = true

    await aiStore.updateProviderConfig(editingProvider.value.id, {
      api_key: editForm.api_key,
      base_url: editForm.base_url,
      models: {
        ...editingProvider.value.models,
        default: editForm.defaultModel
      }
    })

    ElMessage.success('保存成功')
    showEditDialog.value = false
  } catch (error) {
    if (error instanceof Error) {
      ElMessage.error(error.message)
    }
  } finally {
    saving.value = false
  }
}

function openTestDialog(provider: AIProvider) {
  testProvider.value = provider
  showTestDialog.value = true
}

async function runAITest() {
  if (!testProvider.value || !testQuestion.value.trim()) {
    ElMessage.warning('请输入测试问题')
    return
  }

  try {
    await aiStore.queryAI({
      title: testQuestion.value,
      options: testOptions.value,
      provider: testProvider.value.id,
      model: testProvider.value.models.default
    })
  } catch (error) {
    ElMessage.error('测试失败')
  }
}

function openModelManagementDialog(provider: AIProvider) {
  modelManagementProvider.value = provider
  showModelManagementDialog.value = true
}

async function handleProviderAction(command: { action: string; provider: AIProvider }) {
  const { action, provider } = command

  switch (action) {
    case 'setDefault':
      try {
        await aiStore.setDefaultProvider(provider.id)
        ElMessage.success('设置默认服务商成功')
      } catch (error) {
        ElMessage.error('设置失败')
      }
      break

    case 'viewModels':
      ElMessage.info(`查看 ${provider.name} 的模型详情`)
      // 这里可以实现查看模型详情的逻辑
      break

    case 'manageModels':
      openModelManagementDialog(provider)
      break
  }
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

// 生命周期
onMounted(() => {
  aiStore.fetchProviders()
})
</script>

<style scoped>
.provider-list {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-left h2 {
  margin: 0 0 8px 0;
  color: var(--el-text-color-primary);
}

.description {
  margin: 0;
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.provider-card {
  margin-bottom: 20px;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.provider-card.enabled {
  border-color: var(--el-color-primary);
}

.provider-card.is-default {
  border-color: var(--el-color-warning);
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.05) 0%, rgba(230, 162, 60, 0.02) 100%);
}

.provider-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.provider-name {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.provider-info h3 {
  margin: 0;
  color: var(--el-text-color-primary);
}

.provider-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.provider-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.provider-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.value {
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.models-section h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.model-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.model-tag {
  margin-right: 8px;
  margin-bottom: 4px;
}

.provider-actions-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.test-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.test-info {
  background-color: var(--el-bg-color-page);
  padding: 16px;
  border-radius: 8px;
}

.test-info p {
  margin: 4px 0;
}

.test-actions {
  display: flex;
  justify-content: center;
}

.test-result {
  margin-top: 20px;
}

.answer-section {
  margin-top: 16px;
}

.answer-section h4 {
  margin: 0 0 8px 0;
  color: var(--el-text-color-primary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>