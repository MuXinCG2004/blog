---
title: Markdown Showcase - Testing All Features
date: 2025-12-11
tags: [Markdown, Test, Demo]
summary: A comprehensive test of all markdown rendering features including code, math, tables, and more
lang: en
---

# Markdown Showcase

This is a comprehensive demonstration of all supported Markdown features in this blog system.

## 1. Text Formatting

**Bold text** using double asterisks or __double underscores__.

*Italic text* using single asterisks or _single underscores_.

***Bold and italic*** combined.

~~Strikethrough~~ text (if supported).

`Inline code` with backticks.

## 2. Headers

# H1 Header
## H2 Header
### H3 Header
#### H4 Header
##### H5 Header
###### H6 Header

## 3. Lists

### Unordered Lists

- Item 1
- Item 2
  - Nested item 2.1
  - Nested item 2.2
- Item 3

* Alternative syntax
* Using asterisks

### Ordered Lists

1. First item
2. Second item
3. Third item
   1. Nested 3.1
   2. Nested 3.2

### Todo Lists

- [x] Completed task
- [ ] Incomplete task
- [x] Another done task
- [ ] Work in progress

## 4. Links and Images

[Visit GitHub](https://github.com)

[Link with title](https://github.com "GitHub Homepage")

![Alt text for image](https://via.placeholder.com/400x200?text=Sample+Image)

## 5. Blockquotes

> This is a blockquote.
> It can span multiple lines.

> **Note**: Blockquotes can contain other markdown elements.
>
> - Like lists
> - And **formatting**

## 6. Code Blocks

### Python

```python
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
result = fibonacci(10)
print(f"The 10th Fibonacci number is: {result}")
```

### JavaScript

```javascript
// Arrow function example
const multiply = (a, b) => a * b;

// Async/await example
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

### C++

```cpp
#include <iostream>
#include <vector>

class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int minPrice = INT_MAX;
        int maxProfit = 0;

        for (int price : prices) {
            minPrice = min(minPrice, price);
            maxProfit = max(maxProfit, price - minPrice);
        }

        return maxProfit;
    }
};
```

### Bash

```bash
#!/bin/bash

# System information script
echo "System Information"
echo "=================="
uname -a
echo ""
echo "Memory Usage:"
free -h
echo ""
echo "Disk Usage:"
df -h
```

### JSON

```json
{
  "name": "markdown-showcase",
  "version": "1.0.0",
  "author": {
    "name": "Developer",
    "email": "dev@example.com"
  },
  "dependencies": {
    "react": "^18.0.0",
    "tailwindcss": "^3.0.0"
  }
}
```

### SQL

```sql
-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (username, email)
VALUES ('john_doe', 'john@example.com');

-- Query with JOIN
SELECT u.username, p.title
FROM users u
INNER JOIN posts p ON u.id = p.user_id
WHERE u.created_at > '2024-01-01';
```

## 7. Tables

### Simple Table

| Language   | Paradigm       | Year |
|------------|----------------|------|
| Python     | Multi-paradigm | 1991 |
| JavaScript | Multi-paradigm | 1995 |
| Rust       | Multi-paradigm | 2010 |
| Go         | Procedural     | 2009 |

### Aligned Table

| Left Aligned | Center Aligned | Right Aligned |
|:-------------|:--------------:|--------------:|
| Left         | Center         | Right         |
| Text         | Text           | Text          |
| 100          | 200            | 300           |

## 8. Horizontal Rules

---

Three or more hyphens, asterisks, or underscores.

___

Another horizontal rule.

## 9. Mathematics (KaTeX)

### Inline Math

The quadratic formula is $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$.

Einstein's famous equation: $E = mc^2$.

### Block Math

$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$

$$
\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$

$$
\frac{\partial^2 u}{\partial t^2} = c^2 \nabla^2 u
$$

## 10. Emojis

:smile: :tada: :rocket: :fire: :heart: :star:

:check: :x: :warning: :bulb: :book: :memo:

:computer: :coffee: :thumbsup: :eyes: :thinking:

## 11. Nested Structures

1. **First level**
   - Bullet point
   - Another bullet
     - Nested deeper
       - Even deeper
2. **Second level**
   > A blockquote inside a list
   >
   > With multiple lines
3. **Third level**
   ```python
   # Code block in a list
   def hello():
       print("Hello, World!")
   ```

## 12. Complex Example

Here's a complex example combining multiple features:

> **Algorithm Complexity Analysis**
>
> Consider the following Python implementation:
>
> ```python
> def binary_search(arr, target):
>     left, right = 0, len(arr) - 1
>
>     while left <= right:
>         mid = (left + right) // 2
>         if arr[mid] == target:
>             return mid
>         elif arr[mid] < target:
>             left = mid + 1
>         else:
>             right = mid - 1
>
>     return -1
> ```
>
> **Time Complexity**: $O(\log n)$
>
> **Space Complexity**: $O(1)$
>
> | Operation | Best Case | Average Case | Worst Case |
> |-----------|:---------:|:------------:|:----------:|
> | Search    | $O(1)$    | $O(\log n)$  | $O(\log n)$|

## 13. Special Characters

- Ampersand: &
- Less than: <
- Greater than: >
- Quote: "
- Apostrophe: '
- Copyright: ©
- Registered: ®
- Trademark: ™

## 14. HTML Elements (if supported)

<div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;">
    <h3>Styled HTML Block</h3>
    <p>This is raw HTML with inline styles!</p>
</div>

<br>

<details>
<summary>Click to expand</summary>

This content is hidden by default!

- You can include
- Any markdown here
- Including `code`

</details>

## 15. Escape Characters

You can escape special characters with backslash:

- \*Not italic\*
- \**Not bold\**
- \# Not a header
- \`Not code\`

## Conclusion

This showcase demonstrates the full range of Markdown capabilities supported by this blog system. Feel free to use this as a reference for writing your own posts!

---

*Last updated: 2025-12-11*
