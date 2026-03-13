---
name: ai-content-collector
description: Collect and archive AI-related content from the web including articles, blogs, podcasts, and news. Use when the user wants to gather, organize, or track the latest AI developments, research papers, tech news, or industry updates. Triggers on phrases like "收集AI文章", "整理AI资讯", "获取最新AI动态", "archiving AI content", or when daily/regular content aggregation is needed.
---

# AI Content Collector

自动收集、整理和归档 AI 相关的网络内容。

## 工作流程

### 1. 内容发现

使用多种渠道发现 AI 内容：
- **Web 搜索** - 搜索最新 AI 文章、新闻（支持中英文搜索）
- **RSS 订阅** - 监控知名 AI 博客和网站
- **特定来源** - 预设的可靠 AI 资讯源（详见 `references/sources.md`）

#### 推荐搜索组合

**英文搜索**：
```bash
npx ts-node skills/coze-web-search/scripts/search.ts \
  -q "OpenAI Anthropic Google AI latest news" \
  --time-range 1w --count 10
```

**中文搜索**：
```bash
npx ts-node skills/coze-web-search/scripts/search.ts \
  -q "AI人工智能 最新动态" \
  --time-range 1w --count 10
```

#### 权威中文来源推荐

- **央媒**：新华网、央视网、人民网（政策、趋势）
- **财经**：新浪财经、经济参考报（商业、融资）
- **科技**：机器之心、量子位、极客公园（技术、产品）

#### 权威国外来源推荐

- **官方**：OpenAI Blog、Anthropic News、DeepMind Blog（产品、研究）
- **学术**：MIT Technology Review、Nature AI、ArXiv（论文、研究）
- **媒体**：TechCrunch、The Verge、Wired（新闻、分析）
- **通讯**：Import AI、The Batch、TLDR AI（每日简报）
- **播客**：Lex Fridman Podcast、TWIML AI（深度访谈）

### 2. 内容抓取

使用 `coze-web-fetch` 抓取完整内容：

```bash
npx ts-node /workspace/projects/workspace/skills/coze-web-fetch/scripts/fetch.ts \
  -u "<URL>" --format markdown
```

### 3. 内容分类

自动分类：
- **研究论文** - ArXiv、论文解读
- **技术博客** - 技术教程、最佳实践
- **行业新闻** - 产品发布、公司动态
- **播客/视频** - 音频视频内容
- **工具/开源** - 新工具、GitHub 项目

### 4. 信息提取

从内容中提取：
- **标题** - 文章标题
- **摘要** - 核心内容总结
- **关键要点** - 3-5 个 bullet points
- **发布时间** - 文章日期
- **来源** - 网站/作者
- **标签** - AI 子领域（NLP、CV、LLM 等）

### 5. 归档整理

输出格式：
- **每日 Markdown** - 按日期组织的本地文档
- **飞书文档** - 按时间维度组织的知识库（月/周）
- **数据库** - 结构化存储（可选）

#### 时间维度归档（推荐）

由于 AI 资讯具有**时效性**，建议按以下结构组织：

```
📰 AI行业资讯/
├── 📅 2026年3月（当前月）
│   ├── 第1周（3月1-7日）
│   ├── 第2周（3月8-14日）← 最新
│   └── ...
├── 📅 2026年2月（上月）
└── 🗄️ 历史归档（更早月份）
```

**归档规则**：
- **当月内容**：每周更新到当前月份页面
- **上月内容**：次月1日归档到独立月份页面
- **更早内容**：移至历史归档库
- **深度内容**：移至「主题研究」栏目（不受时效限制）

**好处**：
- 快速查看最新资讯（当前月）
- 方便追溯历史（按月份）
- 避免信息过载（自动归档）

## 使用方法

### 手动执行

收集今日 AI 内容：
```bash
python /workspace/projects/workspace/skills/ai-content-collector/scripts/collect_daily.py --date today
```

### 自动执行

通过 cron 或 heartbeat 每天自动运行：
```bash
# 每天上午 8 点执行
0 8 * * * cd /workspace/projects/workspace && python skills/ai-content-collector/scripts/collect_daily.py
```

## 内容源配置

在 `references/sources.md` 中配置可靠的内容源：

> 💡 **提示**：该文件已包含经过实际验证的可靠来源，包括：
> - **国内**：权威央媒、财经媒体、科技媒体
> - **国外**：官方博客、学术期刊、国际媒体、新闻通讯、播客/YouTube
> 
> 详见文件中的「已验证可靠来源」部分和「来源质量评级」

### 默认源

| 类型 | 来源 |
|------|------|
| **研究** | ArXiv CS.AI, Papers With Code, Nature AI |
| **官方博客** | OpenAI, Anthropic, DeepMind, Google AI, Meta AI |
| **国际媒体** | TechCrunch AI, The Verge AI, MIT Tech Review, Wired |
| **新闻通讯** | Import AI, The Batch, TLDR AI |
| **中文-权威** | 新华网、央视网、人民网 |
| **中文-财经** | 新浪财经、澎湃新闻、经济参考报 |
| **中文-科技** | 机器之心、量子位、AI科技评论、极客公园 |
| **中文-综合** | 中国新闻网、中华网 |
| **社区** | Reddit r/MachineLearning, Hacker News |
| **社交媒体** | Twitter/X (@OpenAI, @Anthropic, @ylecun等) |

## 输出格式

### 每日归档文档（本地）

```markdown
# AI 内容归档 - 2026-03-12

## 研究论文
...

## 技术博客
...

## 行业动态
...
```

### 飞书知识库（按时间组织）

**月度汇总页面**：
```markdown
# 📅 2026年3月 - AI行业资讯

## 📊 本月概览
- 资讯数量: XX 条
- 重大事件: X 件
- 融资动态: X 起

## 🔥 本周热点（第X周）
### 1. [标题]
- **日期**: 2026-03-XX
- **来源**: XXX
- **摘要**: ...

## 📅 按周归档
- 第1周（3月1-7日）...
- 第2周（3月8-14日）...

## 📌 标签索引
| 标签 | 文章数 |
|------|--------|
| 🔥 热点 | X |
| 💰 融资 | X |
```

## 脚本工具

### `scripts/collect_daily.py`

主脚本，执行每日收集任务。

参数：
- `--date` - 指定日期 (today/yesterday/YYYY-MM-DD)
- `--output` - 输出格式 (markdown/feishu)
- `--sources` - 指定内容源

### `scripts/search_content.py`

搜索 AI 相关内容。

用法：
```bash
python scripts/search_content.py --query "LLM最新进展" --limit 10
```

### `scripts/extract_keypoints.py`

从文章中提取关键要点。

## 自动化集成

### 添加到 HEARTBEAT.md

```markdown
### 每日 AI 内容收集（每天早上 8:00）
- [ ] 运行 AI 内容收集脚本
- [ ] 整理到当月知识库页面（按周分类）
- [ ] 检查是否需要归档上月内容（每月1日执行）

### 每月归档（每月1日）
- [ ] 将上月内容归档到独立月份页面
- [ ] 更新历史归档索引
- [ ] 创建新的当月页面
```

### 使用 Cron

```bash
# 编辑 crontab
crontab -e

# 添加每日任务
0 9 * * * /usr/bin/python3 /workspace/projects/workspace/skills/ai-content-collector/scripts/collect_daily.py >> /workspace/projects/logs/ai-content.log 2>&1
```

## 注意事项

1. **API 限制** - 搜索和抓取可能有频率限制
2. **内容质量** - 需要人工筛选重要内容
3. **存储空间** - 长期收集会占用磁盘空间
4. **版权注意** - 仅收集公开可访问的内容摘要

## 扩展功能

- **去重检测** - 避免重复收集相同内容
- **重要性评分** - 基于来源、点赞数等排序
- **邮件摘要** - 每日发送摘要邮件
- **飞书推送** - 自动推送到指定群聊
