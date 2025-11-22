import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Question {
  id: number
  question: string
  answer: string
  options?: string
  type?: string
  created_at?: string
}

export interface QuestionInput {
  question_text: string
  answer: string
  options?: string
  question_type?: string
}

export interface QuestionStats {
  total_questions: number
  service_status: {
    database: string
    ai_service: string
  }
}

export const useQuestionStore = defineStore('question', () => {
  // 状态
  const questions = ref<Question[]>([])
  const stats = ref<QuestionStats>({
    total_questions: 0,
    service_status: {
      database: 'unknown',
      ai_service: 'unknown'
    }
  })
  const loading = ref(false)
  const searchKeyword = ref('')
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)

  // 操作
  async function fetchQuestions(page = 1, keyword = '') {
    try {
      loading.value = true
      const params = new URLSearchParams({
        page: page.toString(),
        limit: pageSize.value.toString()
      })

      if (keyword) {
        params.append('keyword', keyword)
      }

      const response = await fetch(`/api/questions?${params}`)
      const data = await response.json()

      if (data.success) {
        // 修复：后端返回的是 data.data.results 而不是 data.data.questions
        questions.value = data.data.results || []
        total.value = data.data.total || 0
        currentPage.value = page
      }
    } catch (error) {
      console.error('获取题目列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  async function fetchQuestionStats() {
    try {
      const response = await fetch('/api/stats')
      const data = await response.json()

      if (data.success) {
        stats.value = data.data
      }
    } catch (error) {
      console.error('获取题目统计失败:', error)
    }
  }

  async function searchQuestions(keyword: string) {
    searchKeyword.value = keyword
    await fetchQuestions(1, keyword)
  }

  async function addQuestion(question: QuestionInput) {
    try {
      // 直接发送数据，字段名已经与后端期望匹配
      const backendQuestion = {
        question_text: question.question_text,
        answer: question.answer,
        options: question.options,
        question_type: question.question_type
      }

      const response = await fetch('/api/questions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(backendQuestion)
      })

      const data = await response.json()
      if (data.success) {
        await fetchQuestions(currentPage.value, searchKeyword.value)
        return true
      } else {
        throw new Error(data.error || '添加题目失败')
      }
    } catch (error) {
      console.error('添加题目失败:', error)
      throw error
    }
  }

  async function updateQuestion(id: number, question: Partial<Question>) {
    try {
      const response = await fetch(`/api/questions/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(question)
      })

      const data = await response.json()
      if (data.success) {
        await fetchQuestions(currentPage.value, searchKeyword.value)
        return true
      } else {
        throw new Error(data.error || '更新题目失败')
      }
    } catch (error) {
      console.error('更新题目失败:', error)
      throw error
    }
  }

  async function deleteQuestion(id: number) {
    try {
      const response = await fetch(`/api/questions/${id}`, {
        method: 'DELETE'
      })

      const data = await response.json()
      if (data.success) {
        await fetchQuestions(currentPage.value, searchKeyword.value)
        return true
      } else {
        throw new Error(data.error || '删除题目失败')
      }
    } catch (error) {
      console.error('删除题目失败:', error)
      throw error
    }
  }

  return {
    // 状态
    questions,
    stats,
    loading,
    searchKeyword,
    currentPage,
    pageSize,
    total,

    // 操作
    fetchQuestions,
    fetchQuestionStats,
    searchQuestions,
    addQuestion,
    updateQuestion,
    deleteQuestion
  }
})