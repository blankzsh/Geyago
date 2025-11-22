<template>
  <div class="question-add">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h2>添加题目</h2>
        <p class="description">向题库中添加新的题目</p>
      </div>
      <div class="header-right">
        <el-button @click="$router.push('/questions/list')">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
      </div>
    </div>

    <!-- 题目表单 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card header="题目信息" class="form-card">
          <el-form
            ref="formRef"
            :model="formData"
            :rules="formRules"
            label-width="120px"
            @submit.prevent="handleSubmit"
          >
            <el-form-item label="题目类型" prop="question_type">
              <el-select
                v-model="formData.question_type"
                placeholder="请选择题目类型"
                style="width: 100%"
                @change="onTypeChange"
              >
                <el-option
                  v-for="type in questionTypes"
                  :key="type.value"
                  :label="type.label"
                  :value="type.value"
                >
                  <div class="type-option">
                    <span>{{ type.label }}</span>
                    <span class="type-desc">{{ type.description }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="问题内容" prop="question_text">
              <el-input
                v-model="formData.question_text"
                type="textarea"
                :rows="4"
                placeholder="请输入问题内容"
                maxlength="2000"
                show-word-limit
              />
            </el-form-item>

            <el-form-item
              v-if="showOptions"
              label="选项"
              prop="options"
            >
              <div class="options-input">
                <div class="options-header">
                  <span>选项格式：</span>
                  <el-radio-group v-model="optionsFormat" @change="convertOptions">
                    <el-radio label="letters">字母标识 (A. 选项 B. 选项)</el-radio>
                    <el-radio label="lines">分行显示 (每行一个选项)</el-radio>
                    <el-radio label="custom">自定义格式</el-radio>
                  </el-radio-group>
                </div>
                <el-input
                  v-model="formData.options"
                  type="textarea"
                  :rows="6"
                  :placeholder="optionsPlaceholder"
                  @input="onOptionsInput"
                />
                <div class="options-preview" v-if="parsedOptions.length > 0">
                  <div class="preview-title">选项预览：</div>
                  <div class="preview-list">
                    <div
                      v-for="(option, index) in parsedOptions"
                      :key="index"
                      class="preview-item"
                    >
                      {{ String.fromCharCode(65 + index) }}. {{ option }}
                    </div>
                  </div>
                </div>
              </div>
            </el-form-item>

            <el-form-item label="正确答案" prop="answer">
              <div class="answer-input">
                <!-- 选择题答案 -->
                <el-select
                  v-if="isChoiceQuestion"
                  v-model="formData.answer"
                  placeholder="请选择正确答案"
                  style="width: 100%"
                >
                  <el-option
                    v-for="(option, index) in parsedOptions"
                    :key="index"
                    :label="`${String.fromCharCode(65 + index)}. ${option}`"
                    :value="String.fromCharCode(65 + index)"
                  />
                </el-select>

                <!-- 判断题答案 -->
                <el-radio-group
                  v-else-if="formData.question_type === 'judgement'"
                  v-model="formData.answer"
                >
                  <el-radio label="对">正确</el-radio>
                  <el-radio label="错">错误</el-radio>
                </el-radio-group>

                <!-- 填空题和简答题答案 -->
                <el-input
                  v-else
                  v-model="formData.answer"
                  type="textarea"
                  :rows="3"
                  :placeholder="answerPlaceholder"
                />
              </div>
            </el-form-item>

            <el-form-item label="标签分类" prop="tags">
              <el-select
                v-model="formData.tags"
                multiple
                filterable
                allow-create
                placeholder="请选择或创建标签"
                style="width: 100%"
              >
                <el-option
                  v-for="tag in commonTags"
                  :key="tag"
                  :label="tag"
                  :value="tag"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="难度等级" prop="difficulty">
              <el-rate
                v-model="formData.difficulty"
                :max="5"
                :texts="['很简单', '简单', '中等', '困难', '很困难']"
                show-text
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleSubmit"
                :loading="submitting"
              >
                <el-icon><Check /></el-icon>
                保存题目
              </el-button>
              <el-button @click="resetForm">
                <el-icon><RefreshLeft /></el-icon>
                重置表单
              </el-button>
              <el-button type="info" @click="saveAsDraft">
                <el-icon><Document /></el-icon>
                保存草稿
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="8">
        <!-- 快速模板 -->
        <el-card header="快速模板" class="templates-card">
          <div class="template-categories">
            <el-tabs v-model="activeCategory">
              <el-tab-pane
                v-for="category in templateCategories"
                :key="category.key"
                :label="category.name"
                :name="category.key"
              >
                <div class="template-list">
                  <div
                    v-for="template in category.templates"
                    :key="template.name"
                    class="template-item"
                    @click="applyTemplate(template)"
                  >
                    <div class="template-name">{{ template.name }}</div>
                    <div class="template-type">{{ getTypeLabel(template.type) }}</div>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-card>

        <!-- 草稿箱 -->
        <el-card header="草稿箱" class="drafts-card">
          <div v-if="drafts.length === 0" class="empty-drafts">
            <el-empty description="暂无草稿" :image-size="60" />
          </div>
          <div v-else class="drafts-list">
            <div
              v-for="(draft, index) in drafts"
              :key="index"
              class="draft-item"
            >
              <div class="draft-content">
                <div class="draft-question">{{ draft.question_text.slice(0, 50) }}...</div>
                <div class="draft-meta">
                  <span class="draft-type">{{ getTypeLabel(draft.question_type) }}</span>
                  <span class="draft-time">{{ formatTime(draft.time) }}</span>
                </div>
              </div>
              <div class="draft-actions">
                <el-button
                  text
                  type="primary"
                  size="small"
                  @click="loadDraft(draft)"
                >
                  加载
                </el-button>
                <el-button
                  text
                  type="danger"
                  size="small"
                  @click="deleteDraft(index)"
                >
                  删除
                </el-button>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 帮助提示 -->
        <el-card header="填写提示" class="tips-card">
          <div class="tips-content">
            <div class="tip-item">
              <el-icon><InfoFilled /></el-icon>
              <span>问题内容要清晰明确，避免歧义</span>
            </div>
            <div class="tip-item">
              <el-icon><InfoFilled /></el-icon>
              <span>选项要互相排斥，避免重叠</span>
            </div>
            <div class="tip-item">
              <el-icon><InfoFilled /></el-icon>
              <span>答案要准确无误，符合题目要求</span>
            </div>
            <div class="tip-item">
              <el-icon><InfoFilled /></el-icon>
              <span>善用标签分类，便于题目管理</span>
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
  ArrowLeft, Check, RefreshLeft, Document, InfoFilled
} from '@element-plus/icons-vue'
import { useQuestionStore } from '@/stores/question'
import type { FormInstance, FormRules } from 'element-plus'

const questionStore = useQuestionStore()

// 响应式数据
const formRef = ref<FormInstance>()
const submitting = ref(false)
const optionsFormat = ref('letters')
const activeCategory = ref('math')
const drafts = ref<any[]>([])

// 表单数据
const formData = reactive({
  question_type: '',
  question_text: '',
  options: '',
  answer: '',
  tags: [] as string[],
  difficulty: 3
})

// 表单规则
const formRules: FormRules = {
  question_type: [
    { required: true, message: '请选择题目类型', trigger: 'change' }
  ],
  question_text: [
    { required: true, message: '请输入问题内容', trigger: 'blur' },
    { min: 5, message: '问题内容至少5个字符', trigger: 'blur' }
  ],
  answer: [
    { required: true, message: '请提供正确答案', trigger: 'blur' }
  ]
}

// 题目类型配置
const questionTypes = [
  { value: 'single', label: '单选题', description: '只有一个正确答案' },
  { value: 'multiple', label: '多选题', description: '可以有多个正确答案' },
  { value: 'judgement', label: '判断题', description: '判断对错' },
  { value: 'fill', label: '填空题', description: '填入正确答案' },
  { value: 'essay', label: '简答题', description: '简要回答问题' }
]

// 常用标签
const commonTags = [
  '数学', '物理', '化学', '生物', '历史', '地理', '语文', '英语',
  '政治', '计算机', '编程', '算法', '数据结构', '网络', '数据库'
]

// 模板分类
const templateCategories = ref([
  {
    key: 'math',
    name: '数学',
    templates: [
      {
        name: '基础加法',
        type: 'single',
        question_text: '1 + 1 等于多少？',
        options: 'A.1 B.2 C.3 D.4',
        answer: 'B',
        tags: ['数学', '基础运算']
      },
      {
        name: '方程求解',
        type: 'single',
        question_text: '求解方程 x + 3 = 7',
        options: 'A.x=2 B.x=3 C.x=4 D.x=5',
        answer: 'C',
        tags: ['数学', '方程']
      }
    ]
  },
  {
    key: 'science',
    name: '科学',
    templates: [
      {
        name: '水的化学式',
        type: 'single',
        question_text: '水的化学式是什么？',
        options: 'A.H2O B.CO2 C.O2 D.N2',
        answer: 'A',
        tags: ['化学', '基础']
      },
      {
        name: '光合作用',
        type: 'essay',
        question_text: '请简述光合作用的过程和意义。',
        options: '',
        answer: '光合作用是植物利用光能将二氧化碳和水转化为有机物的过程。',
        tags: ['生物', '植物']
      }
    ]
  }
])

// 计算属性
const showOptions = computed(() => {
  return ['single', 'multiple'].includes(formData.question_type)
})

const isChoiceQuestion = computed(() => {
  return ['single', 'multiple'].includes(formData.question_type)
})

const optionsPlaceholder = computed(() => {
  switch (optionsFormat.value) {
    case 'letters':
      return '请按字母格式输入选项，例如：\nA. 选项1\nB. 选项2\nC. 选项3\nD. 选项4'
    case 'lines':
      return '请每行输入一个选项，例如：\n选项1\n选项2\n选项3\n选项4'
    default:
      return '请输入选项内容'
  }
})

const answerPlaceholder = computed(() => {
  switch (formData.question_type) {
    case 'fill':
      return '请输入填空题的答案'
    case 'essay':
      return '请输入简答题的参考答案'
    default:
      return '请输入答案'
  }
})

const parsedOptions = computed(() => {
  if (!formData.options) return []

  const lines = formData.options.split('\n').filter(line => line.trim())
  const options: string[] = []

  for (const line of lines) {
    // 匹配字母格式 (A. B. C. D.)
    const letterMatch = line.match(/^[A-Z]\.?\s*(.+)$/)
    if (letterMatch) {
      options.push(letterMatch[1].trim())
      continue
    }

    // 如果是纯文本，直接添加
    if (line.trim()) {
      options.push(line.trim())
    }
  }

  return options
})

// 方法
function onTypeChange() {
  // 清空相关字段
  formData.options = ''
  formData.answer = ''

  // 根据类型设置默认答案格式
  if (formData.question_type === 'judgement') {
    formData.answer = '对'
  }
}

function onOptionsInput() {
  // 如果是选择题且有解析的选项，自动设置答案
  if (isChoiceQuestion.value && parsedOptions.value.length > 0 && !formData.answer) {
    // 这里可以添加智能答案解析逻辑
  }
}

function convertOptions() {
  if (!formData.options) return

  const options = parsedOptions.value
  if (options.length === 0) return

  let newFormat = ''
  switch (optionsFormat.value) {
    case 'letters':
      newFormat = options.map((opt, index) => `${String.fromCharCode(65 + index)}. ${opt}`).join('\n')
      break
    case 'lines':
      newFormat = options.join('\n')
      break
    default:
      return
  }

  formData.options = newFormat
}

async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    submitting.value = true

    const questionData = {
      question_text: formData.question_text,
      answer: formData.answer,
      options: showOptions.value ? formData.options : undefined,
      question_type: formData.question_type
    }

    await questionStore.addQuestion(questionData)
    ElMessage.success('题目添加成功')

    // 清空表单
    resetForm()
  } catch (error) {
    ElMessage.error('添加失败')
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  formData.tags = []
  formData.difficulty = 3
}

function saveAsDraft() {
  const draft = {
    ...formData,
    time: new Date().toISOString()
  }

  drafts.value.unshift(draft)
  if (drafts.value.length > 10) {
    drafts.value = drafts.value.slice(0, 10)
  }

  // 保存到本地存储
  localStorage.setItem('question-drafts', JSON.stringify(drafts.value))
  ElMessage.success('已保存到草稿箱')
}

function loadDraft(draft: any) {
  Object.assign(formData, draft)
  ElMessage.success('草稿已加载')
}

function deleteDraft(index: number) {
  drafts.value.splice(index, 1)
  localStorage.setItem('question-drafts', JSON.stringify(drafts.value))
  ElMessage.success('草稿已删除')
}

function applyTemplate(template: any) {
  Object.assign(formData, template)
  ElMessage.success('模板已应用')
}

function getTypeLabel(type: string) {
  const typeMap: Record<string, string> = {
    single: '单选',
    multiple: '多选',
    judgement: '判断',
    fill: '填空',
    essay: '简答'
  }
  return typeMap[type] || '未知'
}

function formatTime(timeString: string) {
  return new Date(timeString).toLocaleString()
}

// 生命周期
onMounted(() => {
  // 加载草稿
  const savedDrafts = localStorage.getItem('question-drafts')
  if (savedDrafts) {
    try {
      drafts.value = JSON.parse(savedDrafts)
    } catch (error) {
      console.error('加载草稿失败:', error)
    }
  }
})
</script>

<style scoped>
.question-add {
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

.form-card,
.templates-card,
.drafts-card,
.tips-card {
  margin-bottom: 20px;
}

.type-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.type-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.options-input {
  width: 100%;
}

.options-header {
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.options-preview {
  margin-top: 12px;
  padding: 12px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
}

.preview-title {
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--el-text-color-primary);
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preview-item {
  padding: 4px 8px;
  background-color: var(--el-color-primary-light-9);
  border-radius: 4px;
  font-size: 14px;
}

.answer-input {
  width: 100%;
}

.template-categories {
  max-height: 400px;
}

.template-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.template-type {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.empty-drafts {
  padding: 20px;
  text-align: center;
}

.drafts-list {
  max-height: 200px;
  overflow-y: auto;
}

.draft-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.draft-item:last-child {
  border-bottom: none;
}

.draft-question {
  font-size: 14px;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.draft-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.draft-actions {
  display: flex;
  gap: 4px;
}

.tips-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 14px;
  color: var(--el-text-color-regular);
  line-height: 1.5;
}

.tip-item .el-icon {
  color: var(--el-color-primary);
  flex-shrink: 0;
  margin-top: 2px;
}
</style>