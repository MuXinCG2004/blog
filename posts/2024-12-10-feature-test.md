---
title: 功能测试
date: 2024-12-10
tags: [测试, 数学, 代码]
summary: 测试数学公式、代码高亮等功能
---

# 功能测试文章

这是一篇用于测试各种功能的文章。

## 数学公式

### 行内公式

爱因斯坦的质能方程 $E = mc^2$ 是物理学中最著名的方程之一。

二次方程的求根公式是 $x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$。

### 行间公式

欧拉公式：

$$
e^{i\pi} + 1 = 0
$$

麦克斯韦方程组：

$$
\nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}
$$

$$
\nabla \times \mathbf{B} - \frac{1}{c^2}\frac{\partial \mathbf{E}}{\partial t} = \mu_0 \mathbf{J}
$$

## 代码高亮

### Python 代码

```python
def fibonacci(n):
    """计算斐波那契数列"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 测试
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### JavaScript 代码

```javascript
// 异步函数示例
async function fetchData(url) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}
```

### Bash 命令

```bash
# 构建并部署
./deploy.sh build
./deploy.sh push "更新博客"
```

## 其他格式

### 列表

- 无序列表项 1
- 无序列表项 2
  - 嵌套项
- 无序列表项 3

1. 有序列表项 1
2. 有序列表项 2
3. 有序列表项 3

### 引用

> 这是一段引用文字。
> 可以有多行。

### 链接和图片

访问 [GitHub](https://github.com) 了解更多。

---

完。
