# 已添加的搜索来源

## 已配置的科技/媒体来源

### 🤖 AI最新资讯
- **量子位** (qbitai.com) - AI行业资讯
- **36氪** (36kr.com) - 科技创投媒体
- **虎嗅网** (huxiu.com) - 科技商业媒体
- **爱范儿** (ifanr.com) - 数字媒体
- **少数派** (sspai.com) - 效率工具/数字生活
- **知乎** (zhihu.com) - 问答社区
- **机器之心** (jiqizhixin.com) - AI技术媒体

### 🎮 游戏开发
- **游戏葡萄** (youxiputao.com) - 游戏行业媒体
- **少数派** (sspai.com) - 数字生活
- **知乎** (zhihu.com) - 问答社区
- **机核网** (gcores.com) - 游戏文化媒体
- **indienova** (indienova.com) - 独立游戏
- **TapTap** (taptap.com) - 游戏社区

### 🌱 健康生活
- **少数派** (sspai.com) - 生活方式
- **知乎** (zhihu.com) - 问答社区
- **Linux.do** (linux.do) - 生活方式板块
- **丁香医生** (dxy.com) - 医疗健康
- **果壳** (guokr.com) - 科普

---

## 搜索策略

收集器现在会：

1. **从指定网站搜索** - 优先从你提供的媒体来源搜索
2. **使用JSON格式解析** - 正确提取标题、URL、来源、摘要
3. **去重处理** - 避免同一文章被多次收录
4. **通用搜索补充** - 如果指定来源内容不足，会进行通用搜索补充

---

## 配置文件位置

```
skills/content-collector/config/sources.yaml
```

如需修改搜索关键词或添加新来源，编辑此文件即可。
