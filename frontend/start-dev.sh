#!/bin/bash

echo "🚀 启动 Geyago 前端开发服务器..."
echo "📍 当前目录: $(pwd)"

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未检测到 Node.js，请先安装 Node.js (>= 16)"
    echo "📥 下载地址: https://nodejs.org/"
    exit 1
fi

# 显示 Node.js 版本
echo "✅ Node.js 版本: $(node --version)"

# 检查 npm 是否安装
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: 未检测到 npm"
    exit 1
fi

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "📦 检测到未安装依赖，开始安装..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装"
fi

# 检查后端服务是否运行
echo "🔍 检查后端服务状态..."
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✅ 后端服务运行正常"
else
    echo "⚠️  警告: 后端服务未运行，请确保后端服务在 http://localhost:5000 运行"
    echo "💡 可以运行: make run (在后端目录)"
fi

echo ""
echo "🎯 准备启动前端开发服务器..."
echo "📍 访问地址: http://localhost:5173"
echo "📍 API代理: http://localhost:5000"
echo ""
echo "🛑 按 Ctrl+C 停止服务"
echo ""

# 启动开发服务器
npm run dev