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

内容按类型归档到四个模块：

| 模块 | 内容类型 | 关键词 |
|------|----------|--------|
| **📰 AI行业资讯** | 新闻、产品发布、融资动态、行业数据 | OpenAI、Anthropic、GPT、Claude、融资、发布 |
| **🛠️ AI工具与技巧** | 工具推荐、使用教程、Prompt技巧、效率方案 | 工具、教程、技巧、Prompt、How to |
| **📚 主题深度研究** | 技术原理、趋势分析、论文解读、架构设计 | 原理、分析、论文、架构、深度 |
| **💡 经验与案例分享** | 实战经验、踩坑记录、成功案例、最佳实践 | 实践、案例、经验、踩坑、总结 |

**分类规则**:
1. 根据内容主题判断最适合的模块
2. 新闻类 → 📰 AI行业资讯
3. 教程/工具类 → 🛠️ AI工具与技巧
4. 分析/研究类 → 📚 主题深度研究
5. 经验/案例类 → 💡 经验与案例分享

### 4. 信息提取

从内容中提取：
- **标题** - 文章标题
- **摘要** - 核心内容总结
- **关键要点** - 3-5 个 bullet points
- **发布时间** - 文章日期
- **来源** - 网站/作者
- **模块** - 📰 资讯 / 🛠️ 工具技巧 / 📚 深度研究 / 💡 案例分享
- **标签** - AI 子领域（NLP、CV、LLM 等）

### 5. 归档整理

输出格式：
- **每周 Markdown** - 按周组织的本地文档（参考阮一峰《科技爱好者周刊》）
- **飞书文档** - 按周组织的知识库（第X期）
- **数据库** - 结构化存储（可选）

#### 四模块归档结构

根据内容类型分别归档到四个模块：

```
AI最新资讯（首页）
├── 📰 AI行业资讯/           # 新闻、产品发布、融资、行业数据
│   ├── 📅 2026年/
│   │   ├── 📅 3月/
│   │   │   └── 📅 第11周/
│   │   │       └── 📄 3月13日.md
│   │   └── 🗄️ 历史归档/
├── 🛠️ AI工具与技巧/          # 工具推荐、教程、Prompt技巧
├── 📚 主题深度研究/          # 技术原理、趋势分析、论文解读
└── 💡 经验与案例分享/        # 实战经验、踩坑记录、成功案例
```

**归档规则**：
- **📰 资讯模块**：按时间层级（年/月/周/日）归档新闻
- **🛠️ 工具技巧**：按工具类型或更新日期归档
- **📚 深度研究**：按主题或研究方向归档
- **💡 案例分享**：按案例类型或应用场景归档
- **链接引用**：每条内容都附带来源链接，格式 `[标题](URL)`
- **深度内容**：从资讯中提取的精华移至深度研究长期保存

## 使用方法

### 手动执行

收集本周 AI 内容（周刊模式）：
```bash
python /workspace/projects/workspace/skills/ai-content-collector/scripts/collect_weekly.py --week current
```

或指定周数：
```bash
python /workspace/projects/workspace/skills/ai-content-collector/scripts/collect_weekly.py --week 12 --year 2026
```

### 自动执行

通过 cron 或 heartbeat 每周自动运行（推荐周五下午）：
```bash
# 每周五下午 6 点执行
0 18 * * 5 cd /workspace/projects/workspace && python skills/ai-content-collector/scripts/collect_weekly.py
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

### 周刊式归档（推荐）

参考 **《科技爱好者周刊》** 格式，以**周**为单位组织内容：

```markdown
# AI每周精选：第12期（2026-03-17）

## 封面图
![本周封面](图片URL)

## 本周话题
本周最值得关注的热点事件/趋势分析

## 工具/资源

### 1. [工具名称](URL)
一句话描述该工具/资源的用途和特点。
> 来源：[网站名称](URL)

### 2. [工具名称](URL)
...

## 文章

### 1. [文章标题](URL)
**摘要**：核心内容一句话总结
**要点**：
- 要点1
- 要点2
- 要点3
> 来源：[作者/网站](URL) · 2026-03-XX

### 2. [文章标题](URL)
...

## 工具
- [工具1](URL)：简介
- [工具2](URL)：简介

## 本周金句
> "引用本周最有价值的一句话"
> —— [出处](URL)

## 链接引用
- [文章1标题](URL) - 网站名
- [文章2标题](URL) - 网站名
- ...

## 订阅
本期周刊已同步至飞书知识库：[📚 AI每周精选](URL)
```

### 链接引用规范

每条内容必须附带来源链接，格式如下：

```markdown
### [标题](URL)
内容描述...
> 来源：[网站/作者名](URL) · 日期
```

**链接引用原则**：
1. **标题链接**：文章标题直接链接到原文
2. **来源标注**：文末标注来源网站和作者
3. **日期标注**：标注文章发布日期
4. **引用列表**：周刊末尾汇总所有链接

### 飞书知识库（周刊式）

```markdown
# 📅 第12期（2026-03-17）- AI每周精选

## 🔥 本周话题
...

## 🛠️ 工具/资源
...

## 📖 文章
...

## 🔗 链接引用
| 序号 | 标题 | 来源 | 日期 |
|------|------|------|------|
| 1 | [标题](URL) | 网站名 | 03-15 |
| 2 | [标题](URL) | 网站名 | 03-14 |
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

### `scripts/classify_module.py`

自动将内容分类到四个模块（资讯、工具技巧、深度研究、案例分享）。

用法：
```python
from classify_module import classify_content, batch_classify

# 单条分类
module, confidence, reason = classify_content(
    url="https://...",
    title="文章标题",
    content="文章内容"
)

# 批量分类
results = batch_classify([
    {"url": "...", "title": "...", "content": "..."},
    ...
])

# 返回: {"ai-news": [...], "ai-tools": [...], "ai-research": [...], "ai-cases": [...]}
```

## 自动化集成

### 添加到 HEARTBEAT.md

```markdown
### AI 每周精选（每周五下午 6:00）
- [ ] 运行 AI 内容收集脚本（周刊模式）
- [ ] 整理本周内容，添加链接引用
- [ ] 按「工具/资源 + 文章 + 工具」三段式组织
- [ ] 发布新一期周刊到飞书知识库
- [ ] 更新周刊索引和链接引用列表

### 周刊回顾（每月1日）
- [ ] 回顾本月各期周刊
- [ ] 精选重要内容归档到「主题研究」
- [ ] 更新周刊历史索引
```

## 完整工作流：收集 → 分类 → 归档 → 同步

### 步骤1：内容收集

运行周刊收集脚本，获取本周AI相关内容：
```bash
python /workspace/projects/workspace/skills/ai-content-collector/scripts/collect_weekly.py --week current
```

收集结果保存在：
- `memory/ai-content/weekly/weekly-YYYY-WXX.md`

### 步骤2：内容分类

自动按四模块分类：
- **📰 AI行业资讯** - 新闻、产品发布、融资
- **🛠️ AI工具与技巧** - 工具推荐、教程
- **📚 主题深度研究** - 技术原理、论文
- **💡 经验与案例分享** - 实战经验、案例

分类逻辑：
```python
if "发布" in title or "融资" in title or "OpenAI" in title:
    module = "📰 AI行业资讯"
elif "工具" in title or "教程" in title or "技巧" in title:
    module = "🛠️ AI工具与技巧"
elif "论文" in title or "原理" in title or "分析" in title:
    module = "📚 主题深度研究"
elif "案例" in title or "实践" in title or "经验" in title:
    module = "💡 经验与案例分享"
```

### 步骤3：生成本地周刊

按以下格式生成本地 Markdown：
```markdown
# AI每周精选：第X期（YYYY年MM月DD日）

## 📌 本周话题
（人工编辑补充）

## 📖 文章
### 1. [标题](URL)
内容摘要...
> 来源：[网站名](URL)

## 🔗 链接引用
| 序号 | 标题 | 来源 |
|------|------|------|
| 1 | [标题](URL) | 网站名 |
```

### 步骤4：同步到飞书知识库

#### 4.1 获取知识库信息
```bash
# 列出所有知识库空间
feishu_wiki --action spaces

# 获取 AI最新资讯 知识库节点
feishu_wiki --action nodes --space_id 7616519632920251572
```

#### 4.2 创建周刊文档
在「AI最新资讯」知识库下创建新文档：
```bash
feishu_wiki --action create \
  --space_id 7616519632920251572 \
  --parent_node_token <首页节点Token> \
  --title "第X期 - YYYY年MM月DD日" \
  --obj_type docx
```

#### 4.3 写入周刊内容
使用生成的 `obj_token` 写入 Markdown 内容：
```bash
feishu_doc --action write \
  --doc_token <obj_token> \
  --content "# AI每周精选..."
```

### 步骤5：更新操作日志

在 `memory/YYYY-MM-DD.md` 记录同步操作：
```markdown
## 飞书知识库同步
时间：YYYY-MM-DD HH:MM

将第X期（YYYY年MM月DD日）的周刊内容同步到飞书知识库：

### 🤖 AI最新资讯
- 文档标题：第X期 - YYYY年MM月DD日
- Wiki节点：[查看文档](https://xxx.feishu.cn/wiki/xxx)
- 内容：XX条AI相关文章

### 本地备份文件
- `memory/ai-content/weekly/weekly-YYYY-WXX.md`
```

### 完整命令示例

```bash
# 1. 收集内容
python skills/ai-content-collector/scripts/collect_weekly.py --week current

# 2. 同步到飞书（使用 obj_token）
feishu_doc --action write \
  --doc_token CXx8dGQDSoKL3ixkKv5cUaNEn2b \
  --content "$(cat memory/ai-content/weekly/weekly-2026-W11.md)"
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
2. **内容质量** - 周刊需要人工筛选精华内容（宁缺毋滥）
3. **链接有效性** - 定期检查链接是否失效
4. **版权注意** - 仅收集公开可访问的内容摘要，尊重原创
5. **周刊节奏** - 固定每周五发布，培养读者习惯

## 扩展功能

- **去重检测** - 避免重复收集相同内容
- **重要性评分** - 基于来源、点赞数等排序
- **链接检测** - 自动检查失效链接
- **邮件订阅** - 每周发送周刊邮件
- **飞书推送** - 自动推送到指定群聊
- **RSS 输出** - 生成周刊 RSS 订阅源

## 周刊示例

参考阮一峰《科技爱好者周刊》格式：
- 标题：「AI每周精选：第X期（日期）」
- 结构：封面图 → 本周话题 → 工具/资源 → 文章 → 工具 → 金句 → 链接引用
- 风格：简洁、实用、有观点
- 链接：每条内容都有清晰的来源链接
