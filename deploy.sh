#!/bin/bash
#
# 个人主页部署脚本
# 用法: ./deploy.sh [命令] [选项]
#
# 命令:
#   install     安装依赖
#   build       构建静态网站
#   serve       本地预览
#   push        部署到 GitHub Pages
#   help        显示帮助
#
# 示例:
#   ./deploy.sh install      # 首次使用，安装依赖
#   ./deploy.sh build        # 构建网站
#   ./deploy.sh serve        # 本地预览
#   ./deploy.sh push         # 部署到 GitHub
#   ./deploy.sh push "更新博客"  # 带自定义提交信息部署
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 项目目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$PROJECT_DIR/dist"
CONFIG_FILE="$PROJECT_DIR/config.json"
VENV_DIR="$PROJECT_DIR/venv"

# 显示帮助
show_help() {
    echo -e "${CYAN}"
    echo "=================================================="
    echo "        📦 个人主页管理工具"
    echo "=================================================="
    echo -e "${NC}"
    echo -e "${YELLOW}用法:${NC} ./deploy.sh [命令] [选项]"
    echo ""
    echo -e "${YELLOW}命令:${NC}"
    echo "  install     安装项目依赖"
    echo "  build       构建静态网站"
    echo "  serve       启动本地预览服务器"
    echo "  push        部署到 GitHub Pages"
    echo "  new         创建新博客文章"
    echo "  help        显示此帮助信息"
    echo ""
    echo -e "${YELLOW}示例:${NC}"
    echo "  ./deploy.sh install              # 首次使用，安装依赖"
    echo "  ./deploy.sh build                # 构建网站"
    echo "  ./deploy.sh serve                # 本地预览 (http://localhost:8000)"
    echo "  ./deploy.sh push                 # 部署到 GitHub"
    echo "  ./deploy.sh push '更新博客'      # 带自定义提交信息"
    echo "  ./deploy.sh new '我的新文章'     # 创建新博客文章"
    echo ""
}

# 激活虚拟环境
activate_venv() {
    if [ -d "$VENV_DIR" ]; then
        source "$VENV_DIR/bin/activate"
    fi
}

# 安装依赖
install_deps() {
    echo -e "${GREEN}📦 安装项目依赖...${NC}"

    # 创建虚拟环境
    if [ ! -d "$VENV_DIR" ]; then
        echo "   创建虚拟环境..."
        python3 -m venv "$VENV_DIR"
    fi

    # 激活虚拟环境
    source "$VENV_DIR/bin/activate"

    # 安装依赖
    echo "   安装 Python 包..."
    pip install -q -r "$PROJECT_DIR/requirements.txt"
    pip install -q --upgrade Flask Werkzeug

    echo -e "${GREEN}✅ 依赖安装完成!${NC}"
    echo ""
    echo -e "${YELLOW}💡 下一步: 运行 './deploy.sh build' 构建网站${NC}"
}

# 构建网站
build_site() {
    echo -e "${GREEN}🔨 构建静态网站...${NC}"

    activate_venv

    # 使用统一构建脚本
    python3 "$PROJECT_DIR/build.py" --clean

    echo ""
    echo -e "${YELLOW}💡 下一步: 运行 './deploy.sh serve' 本地预览${NC}"
}

# 本地预览
serve_local() {
    echo -e "${GREEN}🌐 启动本地预览服务器...${NC}"

    # 检查 dist 目录
    if [ ! -f "$DIST_DIR/index.html" ]; then
        echo -e "${YELLOW}⚠️  网站未构建，先执行构建...${NC}"
        build_site
    fi

    echo ""
    echo -e "${CYAN}访问 http://localhost:8000 预览网站${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}"
    echo ""

    cd "$DIST_DIR"
    python3 -m http.server 8000
}

# 部署到 GitHub
push_to_github() {
    COMMIT_MSG="${1:-$(date '+%Y-%m-%d %H:%M:%S') 更新}"

    echo -e "${GREEN}🚀 部署到 GitHub Pages...${NC}"

    activate_venv

    # 检查 dist 目录
    if [ ! -f "$DIST_DIR/index.html" ]; then
        echo -e "${YELLOW}⚠️  网站未构建，先执行构建...${NC}"
        build_site
    fi

    # 读取配置
    if [ -f "$CONFIG_FILE" ]; then
        GITHUB_URL=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('github_url', ''))" 2>/dev/null || echo "")
        SITE_URL=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('site_url', ''))" 2>/dev/null || echo "")

        if [ -n "$GITHUB_URL" ]; then
            USERNAME=$(echo "$GITHUB_URL" | sed 's|.*/||')
            GITHUB_REPO="git@github.com:${USERNAME}/${USERNAME}.github.io.git"
        fi
    fi

    if [ -z "$GITHUB_REPO" ]; then
        echo -e "${RED}❌ 无法确定 GitHub 仓库地址${NC}"
        echo "请在 config.json 中配置 github_url"
        exit 1
    fi

    echo "   仓库: $GITHUB_REPO"

    # 进入 dist 目录
    cd "$DIST_DIR"

    # 初始化 git
    if [ ! -d ".git" ]; then
        git init
        git branch -M main
    fi

    # 配置远程仓库
    CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
    if [ "$CURRENT_REMOTE" != "$GITHUB_REPO" ]; then
        git remote remove origin 2>/dev/null || true
        git remote add origin "$GITHUB_REPO"
    fi

    # 提交
    git add -A
    if git diff --staged --quiet; then
        echo -e "${YELLOW}⚠️  没有检测到更改${NC}"
        return 0
    fi

    git commit -m "$COMMIT_MSG"
    git push -u origin main --force

    echo ""
    echo -e "${GREEN}✅ 部署成功!${NC}"
    if [ -n "$SITE_URL" ]; then
        echo -e "🌐 访问: ${BLUE}$SITE_URL${NC}"
    elif [ -n "$USERNAME" ]; then
        echo -e "🌐 访问: ${BLUE}https://${USERNAME}.github.io${NC}"
    fi
    echo ""
    echo -e "${YELLOW}💡 提示: GitHub Pages 可能需要几分钟才能更新${NC}"
}

# 创建新博客文章
new_post() {
    TITLE="${1:-新文章}"
    DATE=$(date '+%Y-%m-%d')
    SLUG=$(echo "$TITLE" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
    FILENAME="$PROJECT_DIR/posts/${DATE}-${SLUG}.md"

    # 确保 posts 目录存在
    mkdir -p "$PROJECT_DIR/posts"

    if [ -f "$FILENAME" ]; then
        echo -e "${RED}❌ 文件已存在: $FILENAME${NC}"
        exit 1
    fi

    cat > "$FILENAME" << EOF
---
title: $TITLE
date: $DATE
tags: [日志]
summary: 文章摘要
---

# $TITLE

在这里开始写你的文章...
EOF

    echo -e "${GREEN}✅ 创建新文章: $FILENAME${NC}"
    echo ""
    echo -e "${YELLOW}💡 编辑完成后运行 './deploy.sh build' 构建网站${NC}"
}

# 主函数
main() {
    cd "$PROJECT_DIR"

    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    case "$1" in
        install)
            install_deps
            ;;
        build)
            build_site
            ;;
        serve|preview|run)
            serve_local
            ;;
        push|deploy)
            push_to_github "$2"
            ;;
        new|post)
            new_post "$2"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知命令: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
