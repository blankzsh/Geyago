# Geyago 智能题库 - 前端管理界面

基于 Vue 3 + Element Plus 构建的现代化 Web 管理界面。

## 🚀 功能特性

### 📊 系统概览
- 实时统计数据展示
- 系统状态监控
- 快速操作入口
- 可视化图表分析

### 🤖 AI 管理
- **AI 服务商管理**: 支持 6 种主流 AI 服务商
  - SiliconFlow (默认)
  - 阿里百炼平台
  - 智谱AI
  - OpenAI
  - Google Gemini
  - Ollama 本地部署
- **动态配置**: 启用/禁用服务商，切换默认提供商
- **模型管理**: 查看和选择不同 AI 模型
- **连接测试**: 实时测试 AI 服务连通性和响应

### 📚 题库管理
- **题目列表**: 分页展示、搜索筛选、批量操作
- **题目添加**: 支持 5 种题型
  - 单选题、多选题、判断题、填空题、简答题
- **智能编辑**: 选项预览、答案验证、模板应用
- **草稿系统**: 自动保存、草稿箱管理

### ⚙️ 系统配置
- **服务器配置**: 端口、调试模式等参数
- **应用配置**: 应用名称、版本、默认AI等
- **API配置**: 超时时间、重试策略等
- **配置管理**: 导入/导出配置文件

## 🛠️ 技术栈

- **框架**: Vue 3 (Composition API)
- **UI库**: Element Plus 2.4+
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **图表**: ECharts + Vue-ECharts
- **构建工具**: Vite
- **语言**: TypeScript
- **样式**: CSS3 + Element Plus 主题

## 📦 安装和运行

### 前置要求
- Node.js >= 16
- npm 或 yarn

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 预览构建结果
```bash
npm run preview
```

## 🌐 访问地址

- 开发环境: http://localhost:5173
- 生产环境: 根据部署配置

## 📁 项目结构

```
src/
├── components/          # 公共组件
├── layout/             # 布局组件
├── router/             # 路由配置
├── stores/             # 状态管理
│   ├── app.ts         # 应用全局状态
│   ├── question.ts    # 题库管理状态
│   └── ai.ts          # AI服务状态
├── views/              # 页面组件
│   ├── Dashboard.vue  # 仪表板
│   ├── ai/           # AI管理页面
│   ├── questions/    # 题库管理页面
│   └── config/       # 系统配置页面
├── App.vue            # 根组件
├── main.ts           # 入口文件
└── env.d.ts          # 类型声明
```

## 🔧 配置说明

### API 代理配置
开发环境下，前端会自动代理 `/api/*` 请求到后端服务器：
```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true
    }
  }
}
```

### 主题配置
支持明暗主题切换，配置保存在本地存储中。

## 📱 响应式设计

- 桌面端：完整功能体验
- 平板端：适配式布局
- 移动端：核心功能支持

## 🔐 安全特性

- API密钥遮蔽显示
- XSS防护
- CSRF保护
- 输入验证和清理

## 🚨 注意事项

1. **API连接**: 确保后端服务在 `http://localhost:5000` 运行
2. **浏览器兼容**: 支持现代浏览器，推荐 Chrome/Firefox/Edge 最新版本
3. **本地存储**: 草稿和主题设置保存在浏览器本地存储中
4. **CORS配置**: 后端需要配置允许前端域名的跨域请求

## 🤝 开发指南

### 添加新页面
1. 在 `src/views/` 中创建页面组件
2. 在 `src/router/index.ts` 中添加路由配置
3. 在侧边栏菜单中添加导航项

### 状态管理
使用 Pinia 进行状态管理：
- 全局状态：`useAppStore()`
- 题库状态：`useQuestionStore()`
- AI状态：`useAIStore()`

### 样式规范
- 优先使用 Element Plus 组件样式
- 自定义样式使用 scoped CSS
- 遵循响应式设计原则

## 🐛 问题反馈

如有问题或建议，请：
1. 检查浏览器控制台错误信息
2. 确认后端服务运行状态
3. 提交 Issue 或联系开发团队

## 📄 许可证

本项目采用 MIT 许可证。