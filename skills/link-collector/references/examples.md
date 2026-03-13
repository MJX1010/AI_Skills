# Link Collector 使用示例

## 示例 1: 基本用法

**用户输入**:
```
帮我整理这些链接：
https://github.com/openclaw/openclaw
https://docs.openclaw.ai
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

**处理步骤**:
1. 提取 3 个 URL
2. 逐个抓取内容
3. 生成 Markdown 文档

**输出文档**:
```markdown
# 链接收藏 - 2026-03-12

共收集 3 个链接

## 📑 目录

- [代码仓库](#代码仓库)
- [文档](#文档)
- [视频](#视频)

---

## 代码仓库

### 1. OpenClaw - GitHub
- **链接**: https://github.com/openclaw/openclaw
- **来源**: github.com
- **摘要**: OpenClaw is an open-source agent framework...

---

## 文档

### 1. OpenClaw Documentation
- **链接**: https://docs.openclaw.ai
- **来源**: docs.openclaw.ai
- **摘要**: Official documentation for OpenClaw...

---

## 视频

### 1. Rick Astley - Never Gonna Give You Up
- **链接**: https://www.youtube.com/watch?v=dQw4w9WgXcQ
- **来源**: youtube.com
- **摘要**: Official music video...
```

## 示例 2: 使用脚本

```bash
# 提取 URL
python scripts/extract_urls.py "这里有链接 https://example.com 和 https://test.com"

# 收集链接并生成文档
python scripts/collect_links.py \
  --urls "https://example.com,https://test.com" \
  --output "我的收藏.md" \
  --title "技术文章收藏"
```

## 示例 3: 飞书文档输出

当用户要求创建飞书文档时：

1. 使用脚本生成 Markdown 内容
2. 使用 `feishu_doc` 工具创建文档
3. 文档结构：
   - 标题: 链接收藏 - {日期}
   - 内容: 分类整理的链接表格
