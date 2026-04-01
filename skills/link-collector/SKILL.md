---
name: link-collector
description: "链接收集与管理工具。支持微信文章抓取、网页内容提取、自动分类归档到知识库。"
author: Workspace
version: 1.0.0
---

# Link Collector - 链接收集工具

专门用于收集、抓取和归档各类链接内容，特别是微信公众号文章。

## 功能特性

- ✅ 微信文章抓取（绕过反爬机制）
- ✅ 自动分类归档到知识库
- ✅ 支持多种输出格式（JSON/Markdown/Text）
- ✅ 去重机制（已收集URL不再重复）

## 使用方法

### 1. 抓取微信文章

```bash
python3 skills/link-collector/scripts/fetch_wechat.py \
  "https://mp.weixin.qq.com/s/xxx" \
  --method playwright \
  --format markdown
```

参数说明：
- `--method`: 抓取方法 (`requests`, `playwright`, `auto`)
- `--format`: 输出格式 (`json`, `markdown`, `txt`)
- `--output`: 输出文件路径（可选）

### 2. 抓取并归档

```bash
python3 skills/link-collector/scripts/archive_wechat.py \
  --url "https://mp.weixin.qq.com/s/xxx" \
  --method playwright \
  --auto-classify
```

参数说明：
- `--url`: 微信文章URL
- `--method`: 抓取方法
- `--auto-classify`: 自动分类
- `--manual`: 强制使用手动模式

### 3. 手动输入模式

当自动抓取被拦截时，使用手动模式：

```bash
python3 skills/link-collector/scripts/archive_wechat.py \
  --url "https://mp.weixin.qq.com/s/xxx" \
  --manual
```

## 分类规则

| 内容类型 | 目标知识库 | 关键词 |
|---------|-----------|--------|
| AI/技术文章 | 🤖 AI最新资讯 | ai, 人工智能, gpt, claude, llm |
| 游戏开发 | 🎮 游戏开发 | game, 游戏, unity, unreal |
| 健康生活 | 🌱 健康生活 | 健康, health, 健身, 运动 |
| 其他 | 🔗 本地链接收藏 | - |

## 存储位置

```
memory/
├── kb-archive/
│   ├── ai-latest-news/    # AI最新资讯
│   ├── game-development/  # 游戏开发
│   └── healthy-living/    # 健康生活
└── link-collection/       # 链接收藏
```

## 依赖要求

```bash
# 基础依赖
pip install requests beautifulsoup4

# Playwright（用于绕过反爬）
pip install playwright
playwright install chromium
```

## 注意事项

⚠️ **重要**: 微信文章抓取请**始终使用专用脚本**，不要尝试 browser 工具（会触发滑块验证）
