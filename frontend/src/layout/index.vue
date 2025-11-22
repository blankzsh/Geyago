<template>
  <el-container class="app-container">
    <!-- 侧边栏 -->
    <el-aside :width="appStore.collapsed ? '64px' : '200px'" class="app-aside">
      <div class="logo">
        <transition name="logo-fade">
          <span v-if="!appStore.collapsed" class="logo-text">Geyago</span>
          <el-icon v-else class="logo-icon"><MagicStick /></el-icon>
        </transition>
      </div>

      <el-menu
        :default-active="$route.path"
        :collapse="appStore.collapsed"
        router
        unique-opened
        class="app-menu"
      >
        <template v-for="route in menuRoutes" :key="route.path">
          <!-- 有子菜单的路由 -->
          <el-sub-menu v-if="route.children && route.children.length > 0" :index="route.path">
            <template #title>
              <el-icon>
                <component :is="route.meta?.icon || 'Menu'" />
              </el-icon>
              <span>{{ route.meta?.title }}</span>
            </template>
            <el-menu-item
              v-for="child in route.children"
              :key="child.path"
              :index="route.path + '/' + child.path"
            >
              <el-icon>
                <component :is="child.meta?.icon || 'Document'" />
              </el-icon>
              <span>{{ child.meta?.title }}</span>
            </el-menu-item>
          </el-sub-menu>

          <!-- 没有子菜单的路由 -->
          <el-menu-item v-else :index="route.path">
            <el-icon>
              <component :is="route.meta?.icon || 'Menu'" />
            </el-icon>
            <span>{{ route.meta?.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <!-- 主体内容 -->
    <el-container class="main-container">
      <!-- 顶部导航栏 -->
      <el-header class="app-header">
        <div class="header-left">
          <el-button
            text
            @click="appStore.toggleSidebar"
            class="collapse-btn"
          >
            <el-icon>
              <Fold v-if="!appStore.collapsed" />
              <Expand v-else />
            </el-icon>
          </el-button>

          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item
              v-for="item in breadcrumbItems"
              :key="item.path"
              :to="{ path: item.path }"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 全局加载状态 -->
          <el-icon v-if="appStore.loading" class="loading-icon">
            <Loading />
          </el-icon>

          <!-- 主题切换 -->
          <el-switch
            v-model="isDark"
            inline-prompt
            :active-icon="Moon"
            :inactive-icon="Sunny"
            @change="toggleTheme"
            class="theme-switch"
          />

          <!-- 版本信息 -->
          <el-tag type="info" size="small">
            v{{ appStore.appInfo?.version || '1.0.0' }}
          </el-tag>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import {
  MagicStick, Menu, Document, DataBoard, List, Plus, Connection,
  Cpu, Setting, Tools, Fold, Expand, Loading, Moon, Sunny
} from '@element-plus/icons-vue'

const route = useRoute()
const appStore = useAppStore()

const isDark = ref(document.documentElement.classList.contains('dark'))

// 菜单路由配置
const menuRoutes = computed(() => {
  return route.matched[0]?.children?.filter(route => route.path !== '') || []
})

// 面包屑导航
const breadcrumbItems = computed(() => {
  const items = []
  const matched = route.matched.filter(item => item.meta && item.meta.title)

  for (const item of matched) {
    if (item.path !== '/' && item.path !== route.path) {
      items.push({
        path: item.path,
        title: item.meta?.title as string
      })
    }
  }

  // 添加当前页面
  if (route.meta?.title) {
    items.push({
      path: route.path,
      title: route.meta.title as string
    })
  }

  return items
})

// 主题切换
function toggleTheme() {
  const html = document.documentElement
  if (isDark.value) {
    html.classList.add('dark')
  } else {
    html.classList.remove('dark')
  }
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

// 监听路由变化
watch(
  () => route.path,
  () => {
    // 可以在这里添加页面切换逻辑
  }
)
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.app-aside {
  background-color: var(--el-bg-color-page);
  border-right: 1px solid var(--el-border-color);
  transition: width 0.3s;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid var(--el-border-color);
  padding: 0 20px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  color: var(--el-color-primary);
}

.logo-icon {
  font-size: 24px;
  color: var(--el-color-primary);
}

.logo-fade-enter-active,
.logo-fade-leave-active {
  transition: opacity 0.3s;
}

.logo-fade-enter-from,
.logo-fade-leave-to {
  opacity: 0;
}

.app-menu {
  border-right: none;
  height: calc(100vh - 60px);
}

.main-container {
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 18px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.theme-switch {
  margin: 0 8px;
}

.app-main {
  background-color: var(--el-bg-color-page);
  padding: 20px;
  overflow-y: auto;
}
</style>