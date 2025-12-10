# Giscus 评论系统配置指南

## 当前状态
- ✅ 仓库已配置: `MuXinCG2004/MuXinCG2004.github.io`
- ⚠️ 需要补充 repo-id 和 category-id

## 配置步骤

### 1. 启用 Discussions
1. 访问: https://github.com/MuXinCG2004/MuXinCG2004.github.io/settings
2. 找到 "Features" 部分
3. 勾选 ✅ "Discussions"

### 2. 获取配置参数
1. 访问: https://giscus.app/zh-CN
2. 输入仓库: `MuXinCG2004/MuXinCG2004.github.io`
3. 选择映射方式: **pathname** (已设置)
4. 选择分类: **Announcements** (推荐，已设置)
5. 复制生成的配置中的以下参数:
   ```
   data-repo-id="R_xxxxx"
   data-category-id="DIC_xxxxx"
   ```

### 3. 更新代码
编辑 `templates/post.html` 第 723-725 行:
```javascript
giscusScript.setAttribute('data-repo-id', 'YOUR_REPO_ID'); // 替换这里
giscusScript.setAttribute('data-category-id', 'YOUR_CATEGORY_ID'); // 替换这里
```

### 4. 重新构建
```bash
python3 build.py
```

### 5. 部署
```bash
./deploy.sh push
```

## 注意事项
- ✅ 仓库必须是公开的
- ✅ 已安装 giscus app: https://github.com/apps/giscus
- ✅ Discussions 功能已启用

## 测试
部署后访问任意博客文章，在底部应该能看到评论区。
