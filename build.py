#!/usr/bin/env python3
"""
统一构建脚本 - 一键生成静态网站
用法: python3 build.py [--serve] [--clean]
"""
import os
import re
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# 项目根目录
ROOT_DIR = Path(__file__).parent.absolute()
DIST_DIR = ROOT_DIR / 'dist'
POSTS_DIR = ROOT_DIR / 'posts'
TEMPLATES_DIR = ROOT_DIR / 'templates'
CONFIG_FILE = ROOT_DIR / 'config.json'

# ============== 配置加载 ==============

def load_config():
    """加载配置文件"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# ============== Markdown 解析 ==============

def parse_frontmatter(content):
    """解析 YAML frontmatter"""
    meta = {'title': '无标题', 'date': '', 'tags': [], 'summary': '', 'lang': 'en'}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml_text = parts[1].strip()
            for line in yaml_text.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    key, val = key.strip(), val.strip()
                    if key == 'tags':
                        meta['tags'] = re.findall(r'[\w\u4e00-\u9fff-]+', val)
                    else:
                        meta[key] = val
            return meta, parts[2].strip()
    return meta, content

def markdown_to_html(md):
    """将 Markdown 转换为 HTML，支持数学公式"""
    # 先保护数学公式，避免被其他处理破坏
    math_blocks = []
    math_inlines = []

    # 保护行间公式 $$...$$
    def save_math_block(match):
        math_blocks.append(match.group(1))
        return f'MATHBLOCK{len(math_blocks)-1}ENDBLOCK'

    md = re.sub(r'\$\$([\s\S]+?)\$\$', save_math_block, md)

    # 保护行内公式 $...$（但不匹配 $$）
    def save_math_inline(match):
        math_inlines.append(match.group(1))
        return f'MATHINLINE{len(math_inlines)-1}ENDINLINE'

    md = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', save_math_inline, md)

    lines = md.split('\n')
    html = []
    in_code = False
    code_lang = ''
    code_lines = []
    in_list = False
    list_type = None
    in_math_block = False
    math_lines = []
    in_table = False
    table_rows = []
    table_aligns = []

    def close_list():
        nonlocal in_list, list_type
        if in_list:
            html.append('</ul>' if list_type == 'ul' else '</ol>')
            in_list = False
            list_type = None

    def close_table():
        nonlocal in_table, table_rows, table_aligns
        if in_table and table_rows:
            table_html = ['<div class="table-wrapper"><table>']
            for i, row in enumerate(table_rows):
                if i == 0:
                    table_html.append('<thead><tr>')
                    for j, cell in enumerate(row):
                        align = table_aligns[j] if j < len(table_aligns) else ''
                        align_attr = f' style="text-align:{align}"' if align else ''
                        table_html.append(f'<th{align_attr}>{process_inline(cell)}</th>')
                    table_html.append('</tr></thead><tbody>')
                else:
                    table_html.append('<tr>')
                    for j, cell in enumerate(row):
                        align = table_aligns[j] if j < len(table_aligns) else ''
                        align_attr = f' style="text-align:{align}"' if align else ''
                        table_html.append(f'<td{align_attr}>{process_inline(cell)}</td>')
                    table_html.append('</tr>')
            table_html.append('</tbody></table></div>')
            html.append(''.join(table_html))
            table_rows = []
            table_aligns = []
            in_table = False

    def process_inline(text):
        # Emoji 支持 :emoji_name:
        emoji_map = {
            ':smile:': '😊', ':tada:': '🎉', ':rocket:': '🚀', ':fire:': '🔥',
            ':heart:': '❤️', ':star:': '⭐', ':check:': '✅', ':x:': '❌',
            ':warning:': '⚠️', ':bulb:': '💡', ':book:': '📚', ':memo:': '📝',
            ':computer:': '💻', ':coffee:': '☕', ':thumbsup:': '👍', ':thumbsdown:': '👎',
            ':eyes:': '👀', ':thinking:': '🤔', ':sunglasses:': '😎', ':muscle:': '💪'
        }
        for emoji_code, emoji in emoji_map.items():
            text = text.replace(emoji_code, emoji)

        # 图片
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)
        # 链接
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        # 粗体
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        # 斜体（注意不要匹配数学公式中的下标）
        text = re.sub(r'(?<![\\a-zA-Z])\*([^*]+?)\*(?![*])', r'<em>\1</em>', text)
        # 行内代码
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        return text

    for line in lines:
        # 代码块
        if line.startswith('```'):
            if in_code:
                escaped_code = '\n'.join(code_lines)
                html.append(f'<div class="code-block"><pre><code class="language-{code_lang}">{escaped_code}</code></pre></div>')
                code_lines = []
                in_code = False
            else:
                close_list()
                code_lang = line[3:].strip() or 'plaintext'
                in_code = True
            continue

        if in_code:
            code_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))
            continue

        # 表格行检测
        if line.strip().startswith('|') and line.strip().endswith('|'):
            close_list()
            cells = [c.strip() for c in line.strip()[1:-1].split('|')]

            # 检查是否是分隔行（如 |:---:|:---:|）
            if all(re.match(r'^:?-+:?$', c.strip()) for c in cells if c.strip()):
                # 解析对齐方式
                table_aligns = []
                for c in cells:
                    c = c.strip()
                    if c.startswith(':') and c.endswith(':'):
                        table_aligns.append('center')
                    elif c.endswith(':'):
                        table_aligns.append('right')
                    else:
                        table_aligns.append('left')
                in_table = True
            else:
                table_rows.append(cells)
                in_table = True
            continue
        elif in_table:
            close_table()

        if not line.strip():
            close_list()
            close_table()
            continue

        if line.startswith('#'):
            close_list()
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                text = process_inline(match.group(2))
                html.append(f'<h{level}>{text}</h{level}>')
                continue

        if line.startswith('>'):
            close_list()
            text = process_inline(line[1:].strip())
            html.append(f'<blockquote>{text}</blockquote>')
            continue

        if re.match(r'^[-*_]{3,}$', line.strip()):
            close_list()
            html.append('<hr>')
            continue

        if re.match(r'^[-*+]\s+', line):
            if not in_list or list_type != 'ul':
                close_list()
                html.append('<ul>')
                in_list = True
                list_type = 'ul'

            # 处理 Todo List： - [ ] 或 - [x]
            todo_match = re.match(r'^[-*+]\s+\[([ xX])\]\s+(.+)$', line)
            if todo_match:
                checked = todo_match.group(1).lower() == 'x'
                text = process_inline(todo_match.group(2))
                checkbox = f'<input type="checkbox" {"checked" if checked else ""} disabled style="margin-right: 0.5em;">'
                html.append(f'<li style="list-style: none;">{checkbox}{text}</li>')
            else:
                text = process_inline(re.sub(r'^[-*+]\s+', '', line))
                html.append(f'<li>{text}</li>')
            continue

        if re.match(r'^\d+\.\s+', line):
            if not in_list or list_type != 'ol':
                close_list()
                html.append('<ol>')
                in_list = True
                list_type = 'ol'
            text = process_inline(re.sub(r'^\d+\.\s+', '', line))
            html.append(f'<li>{text}</li>')
            continue

        close_list()
        # 检查是否是HTML标签（以<开头，以>结尾）
        stripped = line.strip()
        if stripped.startswith('<') and stripped.endswith('>'):
            # 直接添加HTML标签，不包裹在<p>中
            html.append(line)
        elif stripped.startswith('<') and not stripped.endswith('>'):
            # HTML标签可能跨行，也直接添加
            html.append(line)
        elif '<br' in stripped.lower():
            # 包含br标签，直接添加
            html.append(line)
        else:
            # 普通文本，包裹在<p>中
            html.append(f'<p>{process_inline(line)}</p>')

    close_list()
    close_table()
    result = '\n'.join(html)

    # 恢复行间公式
    for i, math in enumerate(math_blocks):
        result = result.replace(f'MATHBLOCK{i}ENDBLOCK', f'<div class="math-block">$${math}$$</div>')

    # 恢复行内公式
    for i, math in enumerate(math_inlines):
        result = result.replace(f'MATHINLINE{i}ENDINLINE', f'${math}$')

    return result

# ============== 模板渲染 ==============

def get_value(obj, path):
    """从嵌套对象中获取值"""
    value = obj
    for part in path.split('.'):
        if isinstance(value, dict):
            value = value.get(part, '')
        elif isinstance(value, list) and part.isdigit():
            idx = int(part)
            value = value[idx] if idx < len(value) else ''
        else:
            return ''
    return value

def render_template(template_content, **kwargs):
    """增强的模板渲染器 - 支持嵌套 for/if"""

    def find_matching_end(text, start_tag, end_tag, start_pos=0):
        """找到匹配的结束标签位置，处理嵌套"""
        depth = 1
        pos = start_pos
        while depth > 0 and pos < len(text):
            next_start = text.find(start_tag, pos)
            next_end = text.find(end_tag, pos)
            if next_end == -1:
                return -1
            if next_start != -1 and next_start < next_end:
                depth += 1
                pos = next_start + len(start_tag)
            else:
                depth -= 1
                if depth == 0:
                    return next_end
                pos = next_end + len(end_tag)
        return -1

    def process_for_loops(text, context):
        """处理 for 循环，支持嵌套"""
        result = text
        while True:
            match = re.search(r'\{%\s*for\s+(\w+)\s+in\s+([\w.]+)\s*%\}', result)
            if not match:
                break

            var_name = match.group(1)
            list_path = match.group(2)
            start_pos = match.end()

            # 找到匹配的 endfor
            end_pos = find_matching_end(result, '{% for', '{% endfor %}', start_pos)
            if end_pos == -1:
                # 尝试不同格式
                end_pos = find_matching_end(result, '{%for', '{%endfor%}', start_pos)
            if end_pos == -1:
                break

            loop_content = result[start_pos:end_pos]
            end_tag_end = result.find('%}', end_pos) + 2

            # 获取列表
            items = get_value(context, list_path)
            if not isinstance(items, list):
                items = []

            # 渲染每个项
            output_parts = []
            for item in items:
                item_context = context.copy()
                item_context[var_name] = item
                # 递归处理循环内容
                rendered = process_for_loops(loop_content, item_context)
                rendered = process_if_conditions(rendered, item_context)
                rendered = replace_variables(rendered, item_context)
                output_parts.append(rendered)

            result = result[:match.start()] + ''.join(output_parts) + result[end_tag_end:]

        return result

    def process_if_conditions(text, context):
        """处理 if 条件，支持嵌套"""
        result = text
        while True:
            match = re.search(r'\{%\s*if\s+([^%]+?)\s*%\}', result)
            if not match:
                break

            condition = match.group(1).strip()
            start_pos = match.end()

            # 找到匹配的 endif
            end_pos = find_matching_end(result, '{% if', '{% endif %}', start_pos)
            if end_pos == -1:
                break

            block_content = result[start_pos:end_pos]
            end_tag_end = result.find('%}', end_pos) + 2

            # 查找 else
            else_match = re.search(r'\{%\s*else\s*%\}', block_content)
            if else_match:
                true_content = block_content[:else_match.start()]
                false_content = block_content[else_match.end():]
            else:
                true_content = block_content
                false_content = ''

            # 评估条件
            condition_result = evaluate_condition(condition, context)
            chosen_content = true_content if condition_result else false_content

            result = result[:match.start()] + chosen_content + result[end_tag_end:]

        return result

    def evaluate_condition(condition, context):
        """评估条件表达式"""
        # 处理 == 比较
        eq_match = re.match(r'([\w.]+)\s*==\s*[\'"](.+?)[\'"]', condition)
        if eq_match:
            value = get_value(context, eq_match.group(1))
            return str(value) == eq_match.group(2)

        # 处理 != 比较
        neq_match = re.match(r'([\w.]+)\s*!=\s*[\'"](.+?)[\'"]', condition)
        if neq_match:
            value = get_value(context, neq_match.group(1))
            return str(value) != neq_match.group(2)

        # 处理 and
        if ' and ' in condition:
            parts = condition.split(' and ')
            return all(get_value(context, p.strip()) for p in parts)

        # 简单真值判断
        value = get_value(context, condition)
        if isinstance(value, list):
            return len(value) > 0
        return bool(value)

    def replace_variables(text, context):
        """替换变量"""
        def replace_var(match):
            var_path = match.group(1).strip()
            # 移除过滤器
            var_path = re.sub(r'\|.*$', '', var_path).strip()
            value = get_value(context, var_path)
            if isinstance(value, list):
                return ', '.join(str(v) for v in value)
            return str(value) if value is not None else ''

        return re.sub(r'\{\{\s*([^}]+?)\s*\}\}', replace_var, text)

    # 主处理流程
    result = template_content
    result = process_for_loops(result, kwargs)
    result = process_if_conditions(result, kwargs)
    result = replace_variables(result, kwargs)

    # 清理未替换的模板标签
    result = re.sub(r'\{%.*?%\}', '', result)

    return result

# ============== 博客构建 ==============

def get_posts():
    """获取所有博客文章"""
    posts = []
    if not POSTS_DIR.exists():
        return posts

    for filepath in POSTS_DIR.glob('*.md'):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        meta, body = parse_frontmatter(content)
        html = markdown_to_html(body)
        posts.append({
            'slug': filepath.stem,
            'title': meta.get('title', '无标题'),
            'date': meta.get('date', ''),
            'tags': meta.get('tags', []),
            'summary': meta.get('summary', ''),
            'lang': meta.get('lang', 'en'),
            'html': html
        })

    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts

def get_related_posts(current_post, all_posts, limit=3):
    """获取相关文章（基于标签相似度）"""
    related = []
    current_tags = set(current_post['tags'])

    for post in all_posts:
        if post['slug'] == current_post['slug']:
            continue

        # 计算标签重叠数量
        post_tags = set(post['tags'])
        common_tags = current_tags & post_tags
        similarity = len(common_tags)

        if similarity > 0:
            related.append({
                'post': post,
                'similarity': similarity
            })

    # 按相似度排序并返回前N篇
    related.sort(key=lambda x: x['similarity'], reverse=True)
    return [item['post'] for item in related[:limit]]

def build_blog():
    """构建博客页面"""
    print("📝 构建博客...")

    config = load_config()
    posts = get_posts()
    print(f"   找到 {len(posts)} 篇文章")

    # 创建 post 目录
    post_dir = DIST_DIR / 'post'
    post_dir.mkdir(exist_ok=True)

    # 读取模板
    blog_template = TEMPLATES_DIR / 'blog.html'
    post_template = TEMPLATES_DIR / 'post.html'

    # 生成博客列表页
    if blog_template.exists():
        with open(blog_template, 'r', encoding='utf-8') as f:
            template = f.read()
        html = render_template(template, config=config, posts=posts)
        with open(DIST_DIR / 'blog.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("   生成 blog.html")

    # 生成文章页面
    if post_template.exists():
        with open(post_template, 'r', encoding='utf-8') as f:
            template = f.read()
        for post in posts:
            # 获取相关文章
            related_posts = get_related_posts(post, posts, limit=3)
            html = render_template(template, config=config, post=post, related_posts=related_posts)
            with open(post_dir / f"{post['slug']}.html", 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"   生成 post/{post['slug']}.html")

    print("   完成!")
    return posts

# ============== 主页构建 ==============

def build_homepage():
    """构建主页 (简化版，使用预生成的模板)"""
    print("🏠 构建主页...")

    config = load_config()
    posts = get_posts()

    # 读取主页模板
    index_template = TEMPLATES_DIR / 'index.html'
    if not index_template.exists():
        print("   错误: templates/index.html 不存在")
        return False

    # 由于主页模板很复杂，需要 Flask 渲染，我们使用 Flask 测试客户端
    try:
        # 动态创建一个简单的 Flask 应用
        from flask import Flask, render_template
        import requests

        app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

        # 获取 GitHub 信息
        github_info = get_github_info(config)

        with app.app_context():
            # 检查背景图片
            background_image = config.get('background', {}).get('image', 'background.jpg')
            background_exists = (ROOT_DIR / background_image).exists()

            html = render_template('index.html',
                                   github_info=github_info,
                                   config=config,
                                   now=datetime.now(),
                                   background_exists=background_exists,
                                   background_path=background_image,
                                   recent_posts=posts[:3])

        with open(DIST_DIR / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html)

        print("   生成 index.html")
        print("   完成!")
        return True

    except Exception as e:
        print(f"   错误: {e}")
        return False

def get_github_info(config):
    """获取 GitHub 用户信息（优化版：减少请求，防止超时）"""
    import requests
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    github_url = config.get('github_url', '')
    username = github_url.rstrip('/').split('/')[-1] if github_url else ''

    default_info = {
        "avatar_url": config.get('avatar', "https://avatars.githubusercontent.com/u/1000000?v=4"),
        "name": config.get('name', 'User'),
        "bio": config.get('bio', ''),
        "total_repos": 0,
        "total_stars": 0,
        "readme_content": "<p>欢迎来到我的主页!</p>",
        "recent_repos": [],
        "activity_data": [0] * 12,
        "activity_labels": [],
        "tech_stack": []
    }

    if not username:
        return default_info

    try:
        print(f"   获取 GitHub 数据: {username}")
        headers = {'Accept': 'application/vnd.github.v3+json'}

        # 设置短超时，防止阻塞
        timeout = 5

        # 获取用户信息
        try:
            resp = requests.get(f'https://api.github.com/users/{username}',
                               headers=headers, timeout=timeout, verify=False)
            if resp.status_code == 200:
                user = resp.json()
                default_info['avatar_url'] = user.get('avatar_url', default_info['avatar_url'])
                default_info['name'] = user.get('name') or username
                default_info['bio'] = config.get('bio') or user.get('bio', '')
        except Exception as e:
            print(f"   获取用户信息失败: {e}")

        # 获取仓库（限制数量）
        try:
            resp = requests.get(f'https://api.github.com/users/{username}/repos?sort=pushed&per_page=5',
                               headers=headers, timeout=timeout, verify=False)
            if resp.status_code == 200:
                repos = resp.json()
                default_info['total_repos'] = len(repos)
                default_info['total_stars'] = sum(r.get('stargazers_count', 0) for r in repos)
                default_info['recent_repos'] = repos[:5]

                # 分析技术栈
                languages = {}
                for repo in repos:
                    lang = repo.get('language')
                    if lang:
                        languages[lang] = languages.get(lang, 0) + 1

                colors = ['#6a11cb', '#2575fc', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
                tech_stack = []
                for i, (lang, _) in enumerate(sorted(languages.items(), key=lambda x: -x[1])[:6]):
                    tech_stack.append({'name': lang, 'color': colors[i % len(colors)]})
                default_info['tech_stack'] = tech_stack
        except Exception as e:
            print(f"   获取仓库信息失败: {e}")

        # 获取 README（限制大小）
        try:
            for branch in ['main', 'master']:
                readme_url = f'https://raw.githubusercontent.com/{username}/{username}/{branch}/README.md'
                resp = requests.get(readme_url, timeout=3, verify=False)
                if resp.status_code == 200:
                    readme_text = resp.text
                    # 限制README大小，防止内存问题
                    if len(readme_text) > 50000:  # 限制50KB
                        readme_text = readme_text[:50000] + "\n\n...(内容过长，已截断)"
                    default_info['readme_content'] = markdown_to_html(readme_text)
                    break
        except Exception as e:
            print(f"   获取README失败: {e}")

        # 获取活动数据（简化版，减少请求）
        try:
            from datetime import datetime, timedelta

            # 只获取第一页事件
            resp = requests.get(f'https://api.github.com/users/{username}/events?per_page=100&page=1',
                               headers=headers, timeout=timeout, verify=False)

            if resp.status_code == 200:
                events = resp.json()

                if events:
                    # 按最近12个月统计
                    now = datetime.now()
                    monthly_commits = [0] * 12

                    # 生成月份标签（使用英文简称，前端会处理国际化）
                    month_labels = []
                    for i in range(11, -1, -1):
                        past_date = now - timedelta(days=i*30)
                        month_labels.append(str(past_date.month))

                    for event in events:
                        if event.get('type') in ['PushEvent', 'CreateEvent', 'IssuesEvent', 'PullRequestEvent']:
                            created_at = event.get('created_at', '')
                            if created_at:
                                try:
                                    event_date = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
                                    months_diff = (now.year - event_date.year) * 12 + (now.month - event_date.month)

                                    if 0 <= months_diff < 12:
                                        month_index = 11 - months_diff
                                        monthly_commits[month_index] += 1
                                except Exception:
                                    pass

                    total_events = sum(monthly_commits)
                    if total_events > 0:
                        default_info['activity_data'] = monthly_commits
                        print(f"   获取到 {total_events} 次活动记录")
        except Exception as e:
            print(f"   获取活动数据失败: {e}")

    except Exception as e:
        print(f"   GitHub API 错误: {e}")

    return default_info

# ============== 清理和资源复制 ==============

def clean():
    """清理构建目录"""
    print("🧹 清理构建目录...")
    if DIST_DIR.exists():
        git_dir = DIST_DIR / '.git'
        git_backup = None
        if git_dir.exists():
            git_backup = ROOT_DIR / '.git_backup_temp'
            shutil.move(str(git_dir), str(git_backup))

        shutil.rmtree(DIST_DIR)

        if git_backup and git_backup.exists():
            DIST_DIR.mkdir()
            shutil.move(str(git_backup), str(git_dir))
        else:
            DIST_DIR.mkdir()
    else:
        DIST_DIR.mkdir()

    # 清理临时文件
    for pattern in ['*.bak', '*.tmp']:
        for f in ROOT_DIR.glob(pattern):
            f.unlink()
            print(f"   删除: {f.name}")

    print("   完成!")

def copy_assets():
    """复制静态资源"""
    print("🖼️  复制静态资源...")
    config = load_config()

    # 复制背景图片
    bg = config.get('background', {}).get('image', 'background.jpg')
    src = ROOT_DIR / bg
    if src.exists():
        shutil.copy(str(src), str(DIST_DIR / bg))
        print(f"   {bg} -> dist/")

    print("   完成!")

def ensure_venv():
    """确保在虚拟环境中运行"""
    # 如果在 CI/CD 环境中（如 Vercel），跳过虚拟环境检查
    if os.environ.get('VERCEL') or os.environ.get('CI'):
        print("📦 检测到 CI/CD 环境，跳过虚拟环境检查")
        return

    venv_dir = ROOT_DIR / 'venv'

    if sys.platform == 'win32':
        venv_python = venv_dir / 'Scripts' / 'python.exe'
        venv_pip = venv_dir / 'Scripts' / 'pip.exe'
    else:
        venv_python = venv_dir / 'bin' / 'python'
        venv_pip = venv_dir / 'bin' / 'pip'

    # 检查是否已经在虚拟环境中
    in_venv = (hasattr(sys, 'real_prefix') or
               (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

    if not in_venv:
        # 如果虚拟环境不存在，创建它
        if not venv_dir.exists():
            print("📦 创建虚拟环境...")
            subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True)

        # 安装依赖
        requirements = ROOT_DIR / 'requirements.txt'
        if requirements.exists():
            print("📦 安装依赖包...")
            subprocess.run([str(venv_pip), 'install', '-q', '-r', str(requirements)], check=True)
            subprocess.run([str(venv_pip), 'install', '-q', '--upgrade', 'Flask', 'Werkzeug'], check=True)

        # 使用虚拟环境的 Python 重新执行脚本
        print("🔄 切换到虚拟环境...\n")
        os.execv(str(venv_python), [str(venv_python)] + sys.argv)

def check_dependencies():
    """检查依赖"""
    # 在 CI/CD 环境中跳过依赖检查
    if os.environ.get('VERCEL') or os.environ.get('CI'):
        print("📦 CI/CD 环境，依赖已由平台管理")
        return

    print("📦 检查依赖...")
    venv_dir = ROOT_DIR / 'venv'

    if sys.platform == 'win32':
        venv_pip = venv_dir / 'Scripts' / 'pip.exe'
    else:
        venv_pip = venv_dir / 'bin' / 'pip'

    requirements = ROOT_DIR / 'requirements.txt'
    if requirements.exists():
        # 静默安装，因为 ensure_venv 已经处理过了
        subprocess.run([str(venv_pip), 'install', '-q', '-r', str(requirements)],
                      check=True, capture_output=True)

    print("   完成!")

def serve():
    """启动本地预览服务器"""
    print("\n🌐 启动本地预览服务器...")
    print(f"   访问 http://localhost:8000 预览网站")
    print("   按 Ctrl+C 停止服务器\n")
    os.chdir(str(DIST_DIR))
    subprocess.run([sys.executable, '-m', 'http.server', '8000'])

# ============== 主函数 ==============

def build(args):
    """执行完整构建"""
    print("\n" + "="*50)
    print("🚀 开始构建个人主页")
    print("="*50 + "\n")

    if args.clean:
        clean()
    elif not DIST_DIR.exists():
        DIST_DIR.mkdir()

    check_dependencies()

    # 构建主页
    if not build_homepage():
        print("\n❌ 主页构建失败!")
        return False

    # 构建博客
    build_blog()

    # 复制资源
    copy_assets()

    # 显示结果
    print("\n" + "="*50)
    print("✅ 构建完成!")
    print("="*50)
    print(f"\n📁 输出目录: {DIST_DIR}")
    print("\n📄 生成的文件:")
    for f in sorted(DIST_DIR.rglob('*')):
        if f.is_file() and '.git' not in str(f):
            rel_path = f.relative_to(DIST_DIR)
            size = f.stat().st_size
            if size > 1024*1024:
                size_str = f"{size/1024/1024:.1f}MB"
            elif size > 1024:
                size_str = f"{size/1024:.1f}KB"
            else:
                size_str = f"{size}B"
            print(f"   {rel_path} ({size_str})")

    if args.serve:
        serve()
    else:
        print("\n💡 提示: 运行 'python3 build.py --serve' 可启动本地预览")
        print("💡 提示: 运行 './deploy.sh push' 可部署到 GitHub Pages")

    return True

def main():
    # 确保在虚拟环境中运行
    ensure_venv()

    parser = argparse.ArgumentParser(description='构建个人主页静态网站')
    parser.add_argument('--serve', '-s', action='store_true', help='构建后启动本地预览服务器')
    parser.add_argument('--clean', '-c', action='store_true', help='构建前清理输出目录')
    parser.add_argument('--only-serve', action='store_true', help='仅启动预览服务器')

    args = parser.parse_args()

    if args.only_serve:
        if not DIST_DIR.exists() or not (DIST_DIR / 'index.html').exists():
            print("❌ dist/ 目录不存在，请先运行构建")
            return 1
        serve()
        return 0

    return 0 if build(args) else 1

if __name__ == '__main__':
    sys.exit(main())
