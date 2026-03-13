---
name: link-collector
description: Collect and organize multiple URLs into structured documents. Use when the user wants to save, bookmark, or organize web links into a readable document format. Triggers on phrases like "整理这些链接", "保存这些网址", "把链接做成文档", "收集这些网页", "batch save links", "organize bookmarks", or when multiple URLs are shared for documentation purposes.
---

# Link Collector

批量抓取网页链接并整理成结构化文档。

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

### Markdown 输出

```markdown
# 链接收藏 - {日期}

## 📑 目录

- [技术文章](#技术文章)
- [视频教程](#视频教程)
- [工具资源](#工具资源)

---

## 技术文章

### 1. {文章标题}
- **链接**: {URL}
- **来源**: {网站名}
- **摘要**: {内容摘要}
- **标签**: {自动分类标签}

---

## 视频教程

### 1. {视频标题}
- **链接**: {URL}
- **平台**: {YouTube/Bilibili}
- **简介**: {视频描述}

---

## 工具资源

### 1. {工具名}
- **链接**: {URL}
- **类型**: {工具类型}
- **简介**: {功能描述}
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
