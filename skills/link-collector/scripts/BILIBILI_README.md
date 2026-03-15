# B站视频内容抓取脚本使用指南

## 脚本说明

参考微信公众号脚本 `fetch_wechat.py` 和 `archive_wechat.py` 实现，支持B站视频的自动抓取和归档。

## 核心脚本

### 1. fetch_bilibili.py - 视频抓取工具

```bash
# 基本用法
python skills/link-collector/scripts/fetch_bilibili.py <B站URL>

# 指定抓取方法
python skills/link-collector/scripts/fetch_bilibili.py <URL> --method api
python skills/link-collector/scripts/fetch_bilibili.py <URL> --method playwright

# 保存到文件
python skills/link-collector/scripts/fetch_bilibili.py <URL> -o video.json

# 输出Markdown格式
python skills/link-collector/scripts/fetch_bilibili.py <URL> --format markdown -o video.md

# 同时归档
python skills/link-collector/scripts/fetch_bilibili.py <URL> --archive
```

**支持的URL格式：**
- 标准BV号: `https://www.bilibili.com/video/BV1xxx`
- 旧版AV号: `https://www.bilibili.com/video/av123456`
- 短链接: `https://b23.tv/xxxxx`

**抓取方法：**
- `api` (推荐): 使用B站公开API，速度快，限制少
- `playwright`: 使用浏览器渲染，适用于API被限制的情况
- `auto` (默认): 先尝试API，失败则使用Playwright

### 2. archive_bilibili.py - 视频归档助手

```bash
# 抓取并归档
python skills/link-collector/scripts/archive_bilibili.py --url <B站URL>

# 从已抓取文件归档
python skills/link-collector/scripts/archive_bilibili.py --file video.json

# 自动分类并归档
python skills/link-collector/scripts/archive_bilibili.py --url <URL> --auto-classify

# 指定归档到知识库
python skills/link-collector/scripts/archive_bilibili.py --url <URL> --kb ai-latest-news

# 同时添加到周刊
python skills/link-collector/scripts/archive_bilibili.py --url <URL> --add-to-weekly
```

## 使用示例

### 示例1：快速抓取视频信息

```bash
python skills/link-collector/scripts/fetch_bilibili.py "https://www.bilibili.com/video/BV1GJ411x7h7"
```

输出：
```
📹 识别到 BV: BV1GJ411x7h7
[方法1] 使用B站API获取: BV1GJ411x7h7...
{
  "title": "【官方 MV】Never Gonna Give You Up - Rick Astley",
  "owner": {"name": "索尼音乐中国"},
  "duration": 213,
  "view_count": 97019509,
  "tags": ["Never Gonna Give You Up", "Rick Astley", "MV"],
  ...
}
```

### 示例2：短链接处理

```bash
python skills/link-collector/scripts/fetch_bilibili.py "https://b23.tv/okL7GcT"
```

自动解析短链接并获取完整视频信息。

### 示例3：归档到知识库

```bash
# AI相关内容
python skills/link-collector/scripts/archive_bilibili.py \
  --url "https://www.bilibili.com/video/BV1cywWztEur" \
  --kb ai-latest-news \
  --add-to-weekly
```

自动分类并归档到链接收藏，同时添加到AI周刊。

## 抓取的信息

脚本会抓取以下视频信息：

| 字段 | 说明 |
|------|------|
| `bvid` | BV号 |
| `title` | 视频标题 |
| `description` | 视频简介 |
| `owner.name` | UP主名称 |
| `duration` | 视频时长(秒) |
| `view_count` | 播放量 |
| `like_count` | 点赞数 |
| `coin_count` | 投币数 |
| `favorite_count` | 收藏数 |
| `share_count` | 分享数 |
| `reply_count` | 评论数 |
| `danmaku_count` | 弹幕数 |
| `tags` | 视频标签 |
| `pubdate` | 发布时间 |
| `pages` | 分P信息 |

## 反爬策略

B站有比较严格的反爬机制，脚本采用以下策略：

1. **优先使用API**: B站有公开的API接口 `/x/web-interface/view`，限制较少
2. **短链接解析**: 自动解析 `b23.tv` 短链接获取真实URL
3. **Playwright备用**: API受限时自动切换到浏览器渲染
4. **请求头伪装**: 模拟真实浏览器请求头
5. **浏览器指纹**: 使用Playwright时禁用自动化特征检测

## 依赖安装

```bash
# 基础依赖
pip install requests beautifulsoup4

# 如果需要Playwright支持
pip install playwright
playwright install chromium
```

## 常见问题

### Q: API返回限制错误？
A: 尝试使用 `--method playwright` 切换为浏览器渲染模式

### Q: 短链接无法解析？
A: 短链接可能已过期，尝试直接使用完整URL

### Q: 某些视频信息不完整？
A: 部分视频（如番剧、电影）可能需要登录才能获取完整信息

### Q: 如何批量处理多个视频？
A: 可以创建一个URL列表文件，使用shell循环处理：

```bash
# urls.txt 每行一个URL
while read url; do
  python skills/link-collector/scripts/archive_bilibili.py --url "$url" --auto-classify
done < urls.txt
```

## 与微信公众号脚本对比

| 功能 | 微信脚本 | B站脚本 |
|------|----------|---------|
| 抓取方法 | requests + playwright | API + playwright |
| 短链接 | 无 | 自动解析 |
| 反爬强度 | 中等 | 较强 |
| 数据格式 | 文章正文 | 视频元数据 |
| 归档位置 | 微信文章 | B站视频 |

## 技术实现

参考微信脚本架构：
- `fetch_wechat.py` → `fetch_bilibili.py`
- `archive_wechat.py` → `archive_bilibili.py`

核心改进：
1. 使用B站API作为主要抓取方式（微信无法使用API）
2. 增加短链接解析功能
3. 增加视频特有的元数据（播放量、弹幕等）
4. 更强的反爬对抗（浏览器指纹伪装）
