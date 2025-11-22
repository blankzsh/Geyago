import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/index.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '系统概览', icon: 'DataBoard' }
      }
    ]
  },
  {
    path: '/questions',
    component: Layout,
    redirect: '/questions/list',
    meta: { title: '题库管理', icon: 'Document' },
    children: [
      {
        path: 'list',
        name: 'QuestionList',
        component: () => import('@/views/questions/QuestionList.vue'),
        meta: { title: '题目列表', icon: 'List' }
      },
      {
        path: 'add',
        name: 'QuestionAdd',
        component: () => import('@/views/questions/QuestionAdd.vue'),
        meta: { title: '添加题目', icon: 'Plus' }
      }
    ]
  },
  {
    path: '/ai',
    component: Layout,
    redirect: '/ai/providers',
    meta: { title: 'AI管理', icon: 'MagicStick' },
    children: [
      {
        path: 'providers',
        name: 'AIProviders',
        component: () => import('@/views/ai/ProviderList.vue'),
        meta: { title: 'AI服务商', icon: 'Connection' }
      },
      {
        path: 'test',
        name: 'AITest',
        component: () => import('@/views/ai/AITest.vue'),
        meta: { title: 'AI测试', icon: 'Cpu' }
      }
    ]
  },
  {
    path: '/config',
    component: Layout,
    redirect: '/config/system',
    meta: { title: '系统配置', icon: 'Setting' },
    children: [
      {
        path: 'system',
        name: 'SystemConfig',
        component: () => import('@/views/config/SystemConfig.vue'),
        meta: { title: '系统配置', icon: 'Tools' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router