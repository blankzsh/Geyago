<template>
  <el-dialog
    v-model="visible"
    :title="`管理 ${provider?.name} 的模型`"
    width="700px"
    @close="handleClose"
  >
    <div v-if="provider" class="model-management">
      <!-- 当前默认模型信息 -->
      <el-card class="default-model-card">
        <template #header>
          <div class="card-header">
            <h4>当前默认模型</h4>
            <el-tag type="primary" size="small">
              {{ provider.models.default || '未设置' }}
            </el-tag>
          </div>
        </template>
        <el-select
          v-model="newDefaultModel"
          placeholder="选择新的默认模型"
          style="width: 100%"
          @change="changeDefaultModel"
        >
          <el-option
            v-for="model in provider.models.available"
            :key="model"
            :label="model"
            :value="model"
          />
        </el-select>
      </el-card>

      <!-- 模型列表 -->
      <el-card class="models-list-card">
        <template #header>
          <div class="card-header">
            <h4>可用模型列表</h4>
            <el-tag type="info" size="small">
              共 {{ provider.models.available.length }} 个模型
            </el-tag>
          </div>
        </template>

        <!-- 添加新模型 -->
        <div class="add-model-section">
          <el-form
            ref="addFormRef"
            :model="addForm"
            :rules="addFormRules"
            inline
            @submit.prevent="addModel"
          >
            <el-form-item prop="modelName">
              <el-input
                v-model="addForm.modelName"
                placeholder="输入新模型名称"
                style="width: 300px"
                clearable
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                @click="addModel"
                :loading="adding"
                :disabled="!addForm.modelName.trim()"
              >
                <el-icon><Plus /></el-icon>
                添加模型
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 模型列表表格 -->
        <el-table
          :data="modelTableData"
          stripe
          style="width: 100%"
          max-height="400"
        >
          <el-table-column prop="name" label="模型名称" min-width="200">
            <template #default="{ row }">
              <div class="model-name-cell">
                <span>{{ row.name }}</span>
                <el-tag
                  v-if="row.name === provider.models.default"
                  type="primary"
                  size="small"
                  class="default-tag"
                >
                  默认
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button
                type="danger"
                size="small"
                text
                @click="removeModel(row.name)"
                :disabled="row.name === provider.models.default"
                :loading="removingModels.includes(row.name)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="provider.models.available.length === 0" class="empty-state">
          <el-empty description="暂无可用模型" />
        </div>
      </el-card>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { useAIStore } from '@/stores/ai'
import type { AIProvider } from '@/stores/ai'

interface Props {
  modelValue: boolean
  provider: AIProvider | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const aiStore = useAIStore()

// 响应式数据
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const adding = ref(false)
const removingModels = ref<string[]>([])
const newDefaultModel = ref('')
const addFormRef = ref<FormInstance>()

// 添加模型表单
const addForm = reactive({
  modelName: ''
})

const addFormRules: FormRules = {
  modelName: [
    { required: true, message: '请输入模型名称', trigger: 'blur' },
    { min: 1, max: 100, message: '模型名称长度应在1-100个字符之间', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (props.provider && props.provider.models.available.includes(value)) {
          callback(new Error('该模型已存在'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 计算属性
const modelTableData = computed(() => {
  if (!props.provider) return []
  return props.provider.models.available.map(modelName => ({
    name: modelName,
    isDefault: modelName === props.provider!.models.default
  }))
})

// 监听provider变化，重置表单
watch(() => props.provider, (newProvider) => {
  if (newProvider) {
    newDefaultModel.value = newProvider.models.default
    addForm.modelName = ''
  }
}, { immediate: true })

// 方法
async function changeDefaultModel(modelName: string) {
  if (!props.provider || !modelName) return

  try {
    // 这里假设有一个更新默认模型的方法
    // 如果没有，可能需要扩展aiStore的方法
    await aiStore.updateProviderConfig(props.provider.id, {
      models: {
        ...props.provider.models,
        default: modelName
      }
    })

    ElMessage.success('默认模型已更新')
  } catch (error) {
    ElMessage.error('更新默认模型失败')
    // 恢复原值
    newDefaultModel.value = props.provider.models.default
  }
}

async function addModel() {
  if (!addFormRef.value || !props.provider) return

  try {
    await addFormRef.value.validate()

    if (!addForm.modelName.trim()) {
      ElMessage.warning('请输入模型名称')
      return
    }

    adding.value = true

    await aiStore.addModelToProvider(props.provider.id, addForm.modelName.trim())

    ElMessage.success('模型添加成功')
    addForm.modelName = ''

    // 刷新提供商数据
    await aiStore.fetchProviders()
  } catch (error) {
    if (error instanceof Error) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('添加模型失败')
    }
  } finally {
    adding.value = false
  }
}

async function removeModel(modelName: string) {
  if (!props.provider) return

  try {
    await ElMessageBox.confirm(
      `确定要删除模型 "${modelName}" 吗？`,
      '确认删除',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      }
    )

    removingModels.value.push(modelName)

    await aiStore.removeModelFromProvider(props.provider.id, modelName)

    ElMessage.success('模型删除成功')

    // 刷新提供商数据
    await aiStore.fetchProviders()
  } catch (error) {
    if (error !== 'cancel') {
      if (error instanceof Error) {
        ElMessage.error(error.message)
      } else {
        ElMessage.error('删除模型失败')
      }
    }
  } finally {
    removingModels.value = removingModels.value.filter(name => name !== modelName)
  }
}

function handleClose() {
  visible.value = false
}
</script>

<style scoped>
.model-management {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.default-model-card,
.models-list-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h4 {
  margin: 0;
  color: var(--el-text-color-primary);
}

.add-model-section {
  margin-bottom: 20px;
  padding: 16px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
}

.model-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.default-tag {
  flex-shrink: 0;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>