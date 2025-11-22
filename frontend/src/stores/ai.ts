import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface AIProvider {
  id: string
  name: string
  enabled: boolean
  base_url: string
  models: {
    default: string
    available: string[]
  }
  status?: string
  last_check?: string
  api_key?: string
  has_api_key?: boolean
  health_status?: boolean
  max_retries?: number
  timeout?: number
}

export interface AIQueryParams {
  title: string
  options?: string
  provider?: string
  model?: string
}

export interface AIQueryResult {
  code: number
  data: string
  msg: string
  source: 'database' | 'ai' | null
  provider?: string
  model?: string
}

export const useAIStore = defineStore('ai', () => {
  // 状态
  const providers = ref<Record<string, AIProvider>>({})
  const currentProvider = ref('')
  const currentModel = ref('')
  const loading = ref(false)
  const testResult = ref<AIQueryResult | null>(null)

  // 操作
  async function fetchProviders() {
    try {
      loading.value = true
      const response = await fetch('/api/ai/providers')
      const data = await response.json()

      if (data.success) {
        // 将后端数据映射到前端AIProvider接口
        const mappedProviders: Record<string, AIProvider> = {}

        for (const [key, providerData] of Object.entries(data.data.providers)) {
          const backendProvider = providerData as any
          mappedProviders[key] = {
            id: key, // 使用对象的键作为ID
            name: backendProvider.name || backendProvider.provider_id || key,
            enabled: backendProvider.enabled || false,
            base_url: backendProvider.base_url || '',
            models: backendProvider.models || { default: '', available: [] },
            status: backendProvider.status,
            last_check: backendProvider.last_check,
            api_key: backendProvider.api_key,
            has_api_key: backendProvider.has_api_key,
            health_status: backendProvider.health_status,
            max_retries: backendProvider.max_retries,
            timeout: backendProvider.timeout
          }
        }

        providers.value = mappedProviders

        // 使用后端返回的默认提供商
        const defaultProvider = data.data.default_provider
        if (defaultProvider && providers.value[defaultProvider]) {
          currentProvider.value = defaultProvider
          currentModel.value = providers.value[defaultProvider].models.default
        } else {
          // 如果没有默认提供商，使用第一个启用的
          const firstEnabled = Object.keys(providers.value).find(key => providers.value[key].enabled)
          if (firstEnabled) {
            currentProvider.value = firstEnabled
            currentModel.value = providers.value[firstEnabled].models.default
          }
        }
      }
    } catch (error) {
      console.error('获取AI服务商列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  async function getProviderModels(providerId: string) {
    try {
      const response = await fetch(`/api/ai/providers/${providerId}/models`)
      const data = await response.json()

      if (data.success) {
        return data.data.models
      }
    } catch (error) {
      console.error('获取AI模型列表失败:', error)
      return []
    }
  }

  async function setDefaultProvider(providerId: string) {
    try {
      const response = await fetch(`/api/ai/providers/${providerId}/set-default`, {
        method: 'POST'
      })

      const data = await response.json()
      if (data.success) {
        currentProvider.value = providerId
        const provider = providers.value[providerId]
        if (provider) {
          currentModel.value = provider.models.default
        }
        return true
      } else {
        throw new Error(data.error || '设置默认AI服务商失败')
      }
    } catch (error) {
      console.error('设置默认AI服务商失败:', error)
      throw error
    }
  }

  async function queryAI(params: AIQueryParams): Promise<AIQueryResult> {
    try {
      loading.value = true
      const queryParams = new URLSearchParams({
        title: params.title
      })

      if (params.options) {
        queryParams.append('options', params.options)
      }
      if (params.provider) {
        queryParams.append('provider', params.provider)
      }
      if (params.model) {
        queryParams.append('model', params.model)
      }

      const response = await fetch(`/api/query?${queryParams}`)
      const result = await response.json()

      // 处理后端API响应格式：{success: true, data: {code, data, msg, source}}
      if (result.success && result.data) {
        testResult.value = {
          code: result.data.code || 0,
          data: result.data.data || '',
          msg: result.data.msg || '',
          source: result.data.source || null
        }
      } else {
        // 处理错误响应
        testResult.value = {
          code: 0,
          data: '',
          msg: result.error || '查询失败',
          source: null
        }
      }

      return testResult.value
    } catch (error) {
      console.error('AI查询失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function updateProviderConfig(providerId: string, config: Partial<AIProvider>) {
    try {
      // 扁平化配置对象以匹配后端API格式
      const requestData = {
        provider_id: providerId,
        ...config
      }

      const response = await fetch('/api/ai/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      })

      const data = await response.json()
      if (data.success) {
        // 更新本地状态
        if (providers.value[providerId]) {
          providers.value[providerId] = { ...providers.value[providerId], ...config }
        }
        return true
      } else {
        throw new Error(data.error || '更新AI服务商配置失败')
      }
    } catch (error) {
      console.error('更新AI服务商配置失败:', error)
      throw error
    }
  }

  function setCurrentProvider(providerId: string) {
    currentProvider.value = providerId
    const provider = providers.value[providerId]
    if (provider) {
      currentModel.value = provider.models.default
    }
  }

  function setCurrentModel(model: string) {
    currentModel.value = model
  }

  async function addModelToProvider(providerId: string, model: string) {
    try {
      const response = await fetch(`/api/ai/providers/${providerId}/models`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ model })
      })

      const data = await response.json()
      if (data.success) {
        // 更新本地状态
        if (providers.value[providerId]) {
          if (!providers.value[providerId].models.available.includes(model)) {
            providers.value[providerId].models.available.push(model)
          }
        }
        return true
      } else {
        throw new Error(data.error || '添加模型失败')
      }
    } catch (error) {
      console.error('添加模型失败:', error)
      throw error
    }
  }

  async function removeModelFromProvider(providerId: string, model: string) {
    try {
      const response = await fetch(`/api/ai/providers/${providerId}/models/${encodeURIComponent(model)}`, {
        method: 'DELETE'
      })

      const data = await response.json()
      if (data.success) {
        // 更新本地状态
        if (providers.value[providerId]) {
          const index = providers.value[providerId].models.available.indexOf(model)
          if (index > -1) {
            providers.value[providerId].models.available.splice(index, 1)
          }
          // 如果删除的是默认模型，需要重新设置默认模型
          if (providers.value[providerId].models.default === model) {
            const available = providers.value[providerId].models.available
            providers.value[providerId].models.default = available.length > 0 ? available[0] : ''
          }
        }
        return true
      } else {
        throw new Error(data.error || '删除模型失败')
      }
    } catch (error) {
      console.error('删除模型失败:', error)
      throw error
    }
  }

  return {
    // 状态
    providers,
    currentProvider,
    currentModel,
    loading,
    testResult,

    // 操作
    fetchProviders,
    getProviderModels,
    setDefaultProvider,
    queryAI,
    updateProviderConfig,
    setCurrentProvider,
    setCurrentModel,
    addModelToProvider,
    removeModelFromProvider
  }
})