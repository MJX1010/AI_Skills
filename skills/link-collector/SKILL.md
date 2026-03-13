---
name: link-collector
description: Collect and organize multiple URLs into structured documents. Use when the user wants to save, bookmark, or organize web links into a readable document format. Triggers on phrases like "整理这些链接", "保存这些网址", "把链接做成文档", "收集这些网页", "batch save links", "organize bookmarks", or when multiple URLs are shared for documentation purposes.
---

# Link Collector

批量抓取网页链接并整理成结构化文档，**智能识别链接适合放入哪个知识库**，并按**层级结构归档**。

## 支持的四个知识库

| 知识库 | 图标 | 说明 | 关键词 |
|--------|------|------|--------|
| **AI最新资讯** | 🤖 | AI行业动态、技术突破 | AI、机器学习、大模型、OpenAI、Claude |
| **游戏开发** | 🎮 | 游戏引擎、开发技术 | Unity、Unreal、游戏开发、独立游戏 |
| **健康生活** | 🌱 | 生活妙招、健康知识 | 健康、运动、饮食、营养、心理健康 |
| **链接收藏** | 🔗 | 通用技术文章、工具 | 其他技术内容 |

---

## 📁 链接归档层级结构

所有收集的链接按以下**四层结构**归档：

```
link-collection/
├── user-links/              # 用户发送的链接
│   ├── 2026/
│   │   ├── 03/             # 月
│   │   │   ├── week-10/    # 周
│   │   │   │   ├── 2026-03-13.md   # 日文档
│   │   │   │   ├── 2026-03-14.md
│   │   │   │   └── week-summary-week-10.md  # 周汇总
│   │   │   └── month-index-03.md    # 月索引
│   │   └── 04/
│   └── archive/            # 历史归档（>1年）
│       └── 2025/
├── self-collected/          # 自动收集的链接
│   └── ... (同上结构)
└── wechat-articles/         # 微信文章
    └── ... (同上结构)
```

### 层级说明

| 层级 | 单位 | 说明 | 示例 |
|------|------|------|------|
| **Level 1** | 年 | 年份文件夹 | `2026/` |
| **Level 2** | 月 | 月份文件夹 | `03/` |
| **Level 3** | 周 | 周次文件夹 | `week-10/` |
| **Level 4** | 日 | 每日文档 | `2026-03-13.md` |
| **Archive** | 年 | 超过1年自动归档 | `archive/2025/` |

### 文档类型

- **日文档**: 每日收集的链接详情
- **周汇总**: 本周所有链接的索引
- **月索引**: 本月所有周汇总的索引
- **年归档**: 超过1年的内容自动归档

## 智能分类

### 自动识别规则

根据以下特征自动判断链接归属：

1. **域名匹配**（权重最高）
   - `openai.com` → AI最新资讯
   - `unity.com` → 游戏开发
   - `github.com` → 根据内容判断

2. **关键词匹配**
   - AI相关：人工智能、机器学习、LLM、GPT → AI最新资讯
   - 游戏相关：游戏开发、Unity、Unreal → 游戏开发
   - 其他 → 链接收藏

3. **内容分析**
   - 抓取链接内容，分析主题
   - 综合评分，选择最匹配的知识库

### 使用分类脚本

```bash
python3 scripts/classify_links.py
```

**输入**：链接列表（URL + 标题 + 内容）
**输出**：按知识库分类的结果

### 分类示例

```python
# 测试链接
test_links = [
    {"url": "https://openai.com/blog/gpt-5", "title": "GPT-5 Released"},
    {"url": "https://unity.com/blog/unity-6", "title": "Unity 6新特性"},
    {"url": "https://example.com/random-article", "title": "随机文章"}
]

# 自动分类
results = batch_classify(test_links)

# 输出结果
{
  "ai-latest-news": [
    {"url": "https://openai.com/blog/gpt-5", ...}
  ],
  "game-dev": [
    {"url": "https://unity.com/blog/unity-6", ...}
  ],
  "link-collection": [
    {"url": "https://example.com/random-article", ...}
  ]
}
```

## 工作流程

### 1. 收集链接

从用户输入中提取所有 URL。支持：
- 纯文本中的链接
- Markdown 格式的链接 `[text](url)`
- 飞书消息中的链接
- 混合内容的链接

### 2. 抓取内容

使用 `coze-web-fetch` 技能抓取每个链接：

```bash
npx ts-node /workspace/projects/workspace/skills/coze-web-fetch/scripts/fetch.ts \
  -u "<URL>" --format markdown
```

### 3. 提取信息

从抓取的内容中提取：
- **标题**: 网页标题
- **摘要**: 前 200 字或第一段内容
- **关键信息**: 根据内容类型提取（文章、视频、产品页等）
- **来源**: 网站域名
- **日期**: 发布日期（如有）

### 4. 分类整理

根据内容自动分类：
- **文章/博客**: 技术文章、新闻报道
- **视频**: YouTube、Bilibili 等
- **产品/工具**: 软件、应用、服务
- **文档**: API 文档、说明书
- **其他**: 无法归类的内容

### 5. 生成文档

输出格式选项：
- **Markdown**: 本地 `.md` 文件
- **飞书文档**: 使用 `feishu_doc` 工具创建

## 使用方法

### 基本用法

用户说："帮我整理这些链接"

1. 提取用户消息中的所有 URL
2. 逐个抓取内容
3. 生成整理后的文档

### 高级用法

用户说："把这些链接整理成飞书文档，按技术分类"

1. 提取 URL
2. 抓取内容
3. **按技术领域分类**（如前端、后端、AI 等）
4. 创建飞书文档

## 文档模板

### Markdown 输出（推荐格式）

参考阮一峰《科技爱好者周刊》的链接引用格式：

```markdown
# 链接收藏 - {日期}

## 📑 目录

- [技术文章](#技术文章)
- [视频教程](#视频教程)
- [工具资源](#工具资源)
- [链接引用](#链接引用)

---

## 技术文章

### 1. [文章标题](URL)
文章摘要内容...

> 来源：[网站名](URL) · 发布日期

### 2. [文章标题](URL)
...

---

## 视频教程

### 1. [视频标题](URL)
视频简介...

> 来源：[YouTube/Bilibili](URL)

---

## 工具资源

### 1. [工具名](URL)
功能简介...

> 来源：[网站名](URL)

---

## 🔗 链接引用

| 序号 | 标题 | 来源 | 链接 |
|------|------|------|------|
| 1 | [文章标题](URL) | 网站名 | URL |
| 2 | [视频标题](URL) | 平台 | URL |
| 3 | [工具名](URL) | 网站名 | URL |
```

### 归档管理器使用

### 添加链接到层级结构

```bash
# 添加用户发送的链接
python3 scripts/archive_manager.py \
  --action add \
  --category user-links \
  --url "https://example.com/article" \
  --title "文章标题" \
  --summary "文章摘要" \
  --source "网站名"

# 添加自动收集的链接
python3 scripts/archive_manager.py \
  --action add \
  --category self-collected \
  --url "https://..." \
  --title "..." \
  --summary "..."

# 添加微信文章
python3 scripts/archive_manager.py \
  --action add \
  --category wechat-articles \
  --url "https://mp.weixin.qq.com/s/xxx" \
  --title "微信文章标题" \
  --summary "摘要" \
  --source "公众号名"
```

### 生成本周汇总

```bash
python3 scripts/archive_manager.py \
  --action week-summary \
  --category user-links
```

### 生成月索引

```bash
python3 scripts/archive_manager.py \
  --action month-index \
  --category user-links
```

### 归档旧内容（>1年）

```bash
python3 scripts/archive_manager.py --action archive
```

### 查看完整结构

```bash
python3 scripts/archive_manager.py --action structure
```

---

## 微信文章抓取 + 自动归档

### 一键抓取并归档微信文章

```bash
# 1. 抓取微信文章
python3 scripts/fetch_wechat.py \
  "https://mp.weixin.qq.com/s/xxx" \
  --method playwright \
  --format json \
  --output /tmp/wechat_article.json

# 2. 解析并归档
python3 scripts/archive_wechat.py \
  --file /tmp/wechat_article.json \
  --auto-classify  # 自动分类到对应知识库
```

### 批量处理微信文章

```bash
# 从文件读取多个URL批量处理
python3 scripts/batch_fetch_wechat.py \
  --urls-file urls.txt \
  --output-dir ./wechat_articles/
```

---

## 链接引用格式说明

**每条内容必须包含**：
1. **标题链接**: `[标题](URL)` - 标题直接链接到原文
2. **来源标注**: `> 来源：[网站名](URL)` - 文末标注来源
3. **日期标注**: 如有发布日期一并标注
4. **引用汇总**: 文档末尾汇总所有链接表格

**示例**：
```markdown
### [OpenAI 发布 GPT-5.4：AI 从"问答"进化为"自主执行"](https://openai.com/blog/gpt-5-4)
OpenAI 发布了 GPT-5.4，首次实现原生电脑操作能力，支持 100 万 Token 上下文...

> 来源：[OpenAI Blog](https://openai.com/blog) · 2026-03-05
```

### 飞书文档输出

使用 `feishu_doc` 工具创建文档：
- 文档标题格式：`链接收藏 {日期}`
- 使用表格整理链接信息
- 添加分类标题

## 脚本工具

### `scripts/collect_links.py`

批量处理链接并生成 Markdown 文档。

用法：
```bash
python scripts/collect_links.py --urls "url1,url2,url3" --output "收藏.md"
```

### `scripts/extract_urls.py`

从文本中提取所有 URL。

用法：
```bash
python scripts/extract_urls.py "文本内容"
```

## 注意事项

1. **抓取限制**: 某些网站可能阻止抓取（如需要登录）
2. **内容长度**: 摘要限制在 200-300 字，避免过长
3. **分类准确性**: 自动分类可能不准确，可在输出中标注
4. **重复检测**: 检查是否有重复链接
5. **链接引用**: **必须**为每条内容添加来源链接，格式 `[标题](URL)` + `> 来源：[网站名](URL)`
6. **引用汇总**: 文档末尾必须添加「🔗 链接引用」表格汇总所有链接

## 链接引用规范

**必须遵循的格式**：

```markdown
### [文章标题](原文链接)
内容摘要...

> 来源：[网站/作者名](原文链接) · 发布日期（如有）
```

**为什么需要链接引用**：
- 尊重原创，便于读者追溯原文
- 方便后续整理和引用
- 符合阮一峰《科技爱好者周刊》的格式规范
- 便于生成引用汇总表格

## 示例

**输入**:
```
帮我整理这些链接：
https://example.com/article1
https://example.com/article2
https://youtube.com/watch?v=xxx
```

**输出**:
创建文档 `链接收藏-2026-03-12.md`，包含：
- 3 个链接的标题和摘要
- 自动分类（2篇技术文章、1个视频）
- 带索引的目录
