---
title: 防止matplotlib中文乱码
date: 2025-12-10
tags: [日志]
summary: 文章摘要
---

# 防止matplotlib中文乱码

在我们使用python进行绘图的同时,我们常常会使用matplotlib库,但其在初次运行时会使得中文乱码,因此我们需要进行一些处理

首先我们需要下载文件字体文件[SimHei](https://www.webfontfree.com/cn/download/SimHei),将其中的.ttf文件夹进行保存

接下来我们创建一个python文件,输入以下代码,直接运行,可以看到程序输出两个路径

```python
import matplotlib
print(matplotlib.matplotlib_fname()) # 获取matplotlib的设置文件夹
print(matplotlib.get_cachedir()) # 获取matplotlib的缓存文件夹
```

代码输出
我们按照路径进入mpl-data文件夹,将我们之前所保存的.ttf文件加入fonts/ttf中
```
fonts images  kpsewhich.lua matplotlibrc  plot_directive sample_data stylelib
```
接下来,我们需要将.matplotlib文件夹下的fontlist-v390.json删除,也就是我们所打印出的第二个路径
最后,加入如下代码
```python
plt.rc('font', family = 'SimHei')
plt.rc('font', size = 16)
plt.rcParams['axes.unicode_minus'] = False		# 显示负号
```
----
感谢观看