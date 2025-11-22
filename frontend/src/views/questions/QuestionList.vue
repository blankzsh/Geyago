<template>
  <div class="question-list">
    <!-- 页面标题和操作 -->
    <div class="page-header">
      <div class="header-left">
        <h2>题目列表</h2>
        <p class="description">管理和查看题库中的所有题目</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="$router.push('/questions/add')">
          <el-icon><Plus /></el-icon>
          添加题目
        </el-button>
        <el-button type="success" @click="exportQuestions">
          <el-icon><Download /></el-icon>
          导出题目
        </el-button>
        <el-button @click="refreshList">
          <el-icon><Refresh /></el-icon>
          刷新列表
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form
        :model="searchForm"
        inline
        @submit.prevent="handleSearch"
      >
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索问题或答案"
            style="width: 300px"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="题目类型">
          <el-select
            v-model="searchForm.type"
            placeholder="请选择题目类型"
            style="width: 150px"
            clearable
          >
            <el-option label="单选题" value="single" />
            <el-option label="多选题" value="multiple" />
            <el-option label="判断题" value="judgement" />
            <el-option label="填空题" value="fill" />
            <el-option label="简答题" value="essay" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 题目表格 -->
    <el-card class="table-card">
      <el-table
        :data="questionStore.questions"
        stripe
        style="width: 100%"
        v-loading="questionStore.loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="question-detail">
              <div class="detail-row">
                <div class="detail-label">问题ID:</div>
                <div class="detail-content">{{ row.id }}</div>
              </div>
              <div class="detail-row">
                <div class="detail-label">完整问题:</div>
                <div class="detail-content">{{ row.question }}</div>
              </div>
              <div v-if="row.options" class="detail-row">
                <div class="detail-label">选项:</div>
                <div class="detail-content">{{ row.options }}</div>
              </div>
              <div class="detail-row">
                <div class="detail-label">答案:</div>
                <div class="detail-content">{{ row.answer }}</div>
              </div>
              <div class="detail-row">
                <div class="detail-label">创建时间:</div>
                <div class="detail-content">{{ formatDateTime(row.created_at) }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="question" label="问题" show-overflow-tooltip min-width="200">
          <template #default="{ row }">
            <div class="question-text">{{ row.question }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="answer" label="答案" show-overflow-tooltip width="150">
          <template #default="{ row }">
            <div class="answer-text">{{ row.answer }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.type)" size="small">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              text
              type="primary"
              size="small"
              @click="editQuestion(row)"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              text
              type="danger"
              size="small"
              @click="deleteQuestion(row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
            <el-button
              text
              type="info"
              size="small"
              @click="testQuestion(row)"
            >
              <el-icon><Cpu /></el-icon>
              测试
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <div class="pagination-left">
          <span class="total-info">
            共 {{ questionStore.total }} 条记录
          </span>
          <el-button
            v-if="selectedQuestions.length > 0"
            type="danger"
            size="small"
            @click="batchDelete"
          >
            <el-icon><Delete /></el-icon>
            批量删除 ({{ selectedQuestions.length }})
          </el-button>
        </div>
        <el-pagination
          v-model:current-page="questionStore.currentPage"
          v-model:page-size="questionStore.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="questionStore.total"
          layout="sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="showEditDialog"
      :title="editingQuestion ? '编辑题目' : '添加题目'"
      width="800px"
    >
      <QuestionForm
        v-if="showEditDialog"
        :question="editingQuestion"
        @submit="handleQuestionSubmit"
        @cancel="showEditDialog = false"
      />
    </el-dialog>

    <!-- AI 测试对话框 -->
    <el-dialog
      v-model="showTestDialog"
      title="AI 测试"
      width="600px"
    >
      <AITestDialog
        v-if="showTestDialog && testingQuestion"
        :question="testingQuestion"
        @close="showTestDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Download, Refresh, Search, RefreshLeft, Edit, Delete, Cpu
} from '@element-plus/icons-vue'
import { useQuestionStore } from '@/stores/question'
import { useAIStore } from '@/stores/ai'
import type { Question } from '@/stores/question'
import QuestionForm from '@/components/QuestionForm.vue'
import AITestDialog from '@/components/AITestDialog.vue'

const questionStore = useQuestionStore()
const aiStore = useAIStore()

// 响应式数据
const selectedQuestions = ref<Question[]>([])
const showEditDialog = ref(false)
const showTestDialog = ref(false)
const editingQuestion = ref<Question | null>(null)
const testingQuestion = ref<Question | null>(null)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  type: ''
})

// 方法
async function refreshList() {
  await questionStore.fetchQuestions(
    questionStore.currentPage,
    searchForm.keyword
  )
}

async function handleSearch() {
  questionStore.currentPage = 1
  await questionStore.fetchQuestions(
    1,
    searchForm.keyword
  )
}

function resetSearch() {
  searchForm.keyword = ''
  searchForm.type = ''
  handleSearch()
}

function handleSelectionChange(selection: Question[]) {
  selectedQuestions.value = selection
}

async function handleSizeChange(size: number) {
  questionStore.pageSize = size
  await refreshList()
}

async function handlePageChange(page: number) {
  await questionStore.fetchQuestions(
    page,
    searchForm.keyword
  )
}

function editQuestion(question: Question) {
  editingQuestion.value = question
  showEditDialog.value = true
}

async function handleQuestionSubmit(questionData: any) {
  try {
    if (editingQuestion.value) {
      // 编辑
      await questionStore.updateQuestion(editingQuestion.value.id, questionData)
      ElMessage.success('更新成功')
    } else {
      // 添加
      await questionStore.addQuestion(questionData)
      ElMessage.success('添加成功')
    }
    showEditDialog.value = false
    editingQuestion.value = null
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function deleteQuestion(question: Question) {
  try {
    await ElMessageBox.confirm(
      `确定要删除题目 "${question.question.slice(0, 50)}..." 吗？`,
      '确认删除',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      }
    )

    await questionStore.deleteQuestion(question.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function batchDelete() {
  if (selectedQuestions.value.length === 0) return

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedQuestions.value.length} 道题目吗？`,
      '确认批量删除',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      }
    )

    const promises = selectedQuestions.value.map(q => questionStore.deleteQuestion(q.id))
    await Promise.all(promises)

    ElMessage.success('批量删除成功')
    selectedQuestions.value = []
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

function testQuestion(question: Question) {
  testingQuestion.value = question
  showTestDialog.value = true
}

async function exportQuestions() {
  try {
    // 这里需要实现导出功能
    ElMessage.success('导出功能开发中...')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 工具方法
function getTypeLabel(type?: string) {
  const typeMap: Record<string, string> = {
    single: '单选',
    multiple: '多选',
    judgement: '判断',
    fill: '填空',
    essay: '简答'
  }
  return typeMap[type || 'unknown'] || '未知'
}

function getTypeColor(type?: string) {
  const colorMap: Record<string, string> = {
    single: 'primary',
    multiple: 'success',
    judgement: 'warning',
    fill: 'info',
    essay: 'danger'
  }
  return colorMap[type || 'unknown'] || ''
}

function formatDateTime(dateString?: string) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString()
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    questionStore.fetchQuestions(),
    aiStore.fetchProviders()
  ])
})
</script>

<style scoped>
.question-list {
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

.header-right {
  display: flex;
  gap: 12px;
}

.search-card,
.table-card {
  margin-bottom: 20px;
}

.question-detail {
  padding: 20px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
}

.detail-row {
  display: flex;
  margin-bottom: 12px;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-label {
  width: 80px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  flex-shrink: 0;
}

.detail-content {
  flex: 1;
  color: var(--el-text-color-regular);
  line-height: 1.5;
}

.question-text,
.answer-text {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pagination-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.pagination-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.total-info {
  color: var(--el-text-color-regular);
  font-size: 14px;
}
</style>