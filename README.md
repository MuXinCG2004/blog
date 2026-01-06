# 个人博客系统

基于 Python 的静态博客生成器，部署到 GitHub Pages。

## 快速开始

```bash
# 1. 安装依赖
./deploy.sh install

# 2. 构建网站
./deploy.sh build

# 3. 本地预览
./deploy.sh serve

# 4. 部署到 GitHub Pages
./deploy.sh push
```

## 命令说明

| 命令 | 说明 |
|------|------|
| `./deploy.sh install` | 安装 Python 依赖 |
| `./deploy.sh build` | 构建静态网站到 `dist/` |
| `./deploy.sh serve` | 启动本地预览服务器 (http://localhost:8000) |
| `./deploy.sh push` | 部署到 GitHub Pages |
| `./deploy.sh push "提交信息"` | 带自定义提交信息部署 |
| `./deploy.sh new "文章标题"` | 创建新博客文章 |
| `./deploy.sh help` | 显示帮助 |

## 目录结构

```
blog/
├── posts/              # 博客文章 (Markdown)
│   ├── Algorithm/      # 算法分类
│   ├── Development/    # 开发分类
│   └── Life/           # 生活分类
├── templates/          # HTML 模板
├── config.json         # 网站配置
├── build.py            # 构建脚本
├── deploy.sh           # 部署工具
├── background.png      # 背景图片
└── dist/               # 构建输出 (自动生成)
```

## 写文章

1. 创建新文章:
   ```bash
   ./deploy.sh new "我的新文章"
   ```

2. 或手动在 `posts/` 目录下创建 `.md` 文件，格式:
   ```markdown
   ---
   title: 文章标题
   date: 2024-01-01
   tags: [标签1, 标签2]
   summary: 文章摘要
   ---

   # 正文内容
   ```

3. 构建并预览:
   ```bash
   ./deploy.sh build
   ./deploy.sh serve
   ```

## 个性化配置

编辑 `config.json` 自定义你的博客：

### 基本信息

| 字段 | 说明 | 示例 |
|------|------|------|
| `name` | 显示名称 | `"张三"` |
| `bio` | 个人简介 | `"前端开发者"` |
| `avatar` | 头像 URL | `"https://github.com/xxx.png"` |
| `github_url` | GitHub 主页 | `"https://github.com/xxx"` |
| `site_url` | 网站地址 | `"https://xxx.github.io"` |
| `introduction_file` | 首页介绍文件 | `"Introduction.md"` |
| `recent_posts_count` | 首页显示文章数 | `3` |

### 深色模式

```json
"dark_mode": "auto"  // 可选: "auto", "light", "dark"
```

### 主题颜色

```json
"theme": {
  "primary_color": "#0d9488",      // 主色调 (浅色模式)
  "secondary_color": "#06b6d4",    // 次要颜色 (浅色模式)
  "dark_primary_color": "#14b8a6", // 主色调 (深色模式)
  "dark_secondary_color": "#22d3ee" // 次要颜色 (深色模式)
}
```

常用配色参考:
- 青色系: `#0d9488` / `#06b6d4`
- 蓝色系: `#2563eb` / `#3b82f6`
- 紫色系: `#7c3aed` / `#8b5cf6`
- 绿色系: `#059669` / `#10b981`

### 背景设置

```json
"background": {
  "image": "background.png",       // 背景图片文件名 (放在根目录)
  "blur": 4,                       // 模糊程度 (0-10)
  "overlay_opacity": 0.6,          // 遮罩透明度 (0-1)
  "overlay_color": "#f3f4f6",      // 遮罩颜色 (浅色模式)
  "dark_overlay_color": "#121212"  // 遮罩颜色 (深色模式)
}
```

### 社交链接

填写后会在页面显示对应图标：

```json
"contact": {
  "qq": "123456789",
  "wechat": "微信号",
  "bilibili": "https://space.bilibili.com/xxx",
  "douyin": "抖音号",
  "xiaohongshu": "小红书号"
}
```

留空 `""` 则不显示该图标。

### 完整配置示例

```json
{
  "name": "你的名字",
  "bio": "一句话介绍",
  "avatar": "https://github.com/你的用户名.png",
  "github_url": "https://github.com/你的用户名",
  "site_url": "https://你的用户名.github.io",
  "dark_mode": "auto",
  "introduction_file": "Introduction.md",
  "theme": {
    "primary_color": "#0d9488",
    "secondary_color": "#06b6d4",
    "dark_primary_color": "#14b8a6",
    "dark_secondary_color": "#22d3ee"
  },
  "background": {
    "image": "background.png",
    "blur": 4,
    "overlay_opacity": 0.6,
    "overlay_color": "#f3f4f6",
    "dark_overlay_color": "#121212"
  },
  "contact": {
    "qq": "",
    "wechat": "",
    "bilibili": "",
    "douyin": "",
    "xiaohongshu": ""
  },
  "recent_posts_count": 3
}
```

修改配置后记得重新构建: `./deploy.sh build`

## 部署到 GitHub Pages

1. 创建名为 `<你的用户名>.github.io` 的仓库
2. 配置 `config.json` 中的 `github_url` 和 `site_url`
3. 运行 `./deploy.sh push`

网站将部署到 `https://<你的用户名>.github.io`

## 依赖

- Python 3.x
- 依赖包见 `requirements.txt`
