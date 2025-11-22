import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface AppInfo {
  name: string
  version: string
  homepage: string
}

export interface ServerConfig {
  host: string
  port: number
  debug: boolean
}

export const useAppStore = defineStore('app', () => {
  // 状态
  const appInfo = ref<AppInfo>({
    name: 'Geyago智能题库',
    version: '1.0.0',
    homepage: 'https://toni.wang/'
  })

  const serverConfig = ref<ServerConfig>({
    host: '0.0.0.0',
    port: 5000,
    debug: false
  })

  const loading = ref(false)
  const collapsed = ref(false)

  // 操作
  async function initializeApp() {
    try {
      loading.value = true
      await Promise.all([
        fetchAppConfig(),
        fetchSystemStats()
      ])
    } finally {
      loading.value = false
    }
  }

  async function fetchAppConfig() {
    try {
      const response = await fetch('/api/config')
      const data = await response.json()
      if (data.success) {
        appInfo.value = data.data.app
        serverConfig.value = data.data.server
      }
    } catch (error) {
      console.error('获取应用配置失败:', error)
    }
  }

  async function fetchSystemStats() {
    try {
      const response = await fetch('/api/stats')
      const data = await response.json()
      if (data.success) {
        // 可以在这里处理系统统计数据
        console.log('系统统计:', data.data)
      }
    } catch (error) {
      console.error('获取系统统计失败:', error)
    }
  }

  function toggleSidebar() {
    collapsed.value = !collapsed.value
  }

  return {
    // 状态
    appInfo,
    serverConfig,
    loading,
    collapsed,

    // 操作
    initializeApp,
    fetchAppConfig,
    fetchSystemStats,
    toggleSidebar
  }
})