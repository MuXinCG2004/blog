#!/bin/bash
# Vercel 构建脚本

set -e  # 遇到错误立即退出

echo "📦 开始构建博客..."

# 检查 Python 版本
python3 --version

# 直接运行构建脚本（不需要虚拟环境，Vercel 已经安装了依赖）
python3 build.py --clean

echo "✅ 构建完成！"
