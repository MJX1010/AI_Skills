# 自定义内容来源指南

## 问题说明

之前第11期和第12期内容重复的原因是：
- 收集器使用了**硬编码的示例数据**
- 当搜索没有返回结果时，会返回固定的示例文章

现已修复：
- ✅ 收集器不再使用示例数据
- ✅ 支持从配置文件读取搜索关键词
- ✅ 支持去重，避免重复内容

---

## 配置方法

### 方法一：修改搜索关键词（推荐）

编辑配置文件：
```bash
nano skills/content-collector/config/sources.yaml
```

修改搜索关键词：
```yaml
ai-latest-news:
  search_queries:
    - "OpenAI GPT-5 最新发布"  # 修改为你想要的关键词
    - "Google Gemini AI 更新"
    - "Claude Anthropic 新功能"
    - "人工智能大模型 突破"
```

### 方法二：添加 RSS 订阅源

在配置文件中添加 RSS：
```yaml
ai-latest-news:
  rss_feeds:
    - name: "机器之心"
      url: "https://www.jiqizhixin.com/rss"
    - name: "量子位"
      url: "https://www.qbitai.com/feed"
```

### 方法三：手动添加文章

直接添加链接到周刊：
```bash
# 添加单篇文章
python skills/link-collector/scripts/collect_links.py \
  --url "https://example.com/article" \
  --kb ai-latest-news
```

### 方法四：直接编辑周刊文件

直接编辑 Markdown 文件：
```bash
# AI资讯
nano memory/ai-content/weekly/weekly-2026-W13.md

# 游戏开发
nano memory/game-content/weekly/game-weekly-2026-W13.md

# 健康生活
nano memory/health-content/weekly/health-weekly-2026-W13.md
```

---

## 配置文件位置

| 文件 | 说明 |
|------|------|
| `skills/content-collector/config/sources.yaml` | 搜索关键词和RSS配置 |
| `config/content_sources.yaml` | 备份配置（用户自定义） |

---

## 搜索关键词建议

### 🤖 AI最新资讯
- `OpenAI GPT-5 最新发布 2026`
- `Claude Anthropic 新功能`
- `Google Gemini AI 更新`
- `人工智能大模型 技术突破`
- `AI安全 AGI 研究进展`

### 🎮 游戏开发
- `Unity 2026 新功能 更新`
- `Unreal Engine 5 教程`
- `Godot 引擎 独立游戏开发`
- `游戏设计 关卡设计`
- `独立游戏发布 Steam`

### 🌱 健康生活
- `科学饮食 营养健康 2026`
- `运动健身 锻炼方法`
- `心理健康 压力管理`
- `睡眠质量 改善方法`
- `生活妙招 小窍门`

---

## 权威来源推荐

### AI资讯
- OpenAI Blog (openai.com)
- Anthropic News (anthropic.com)
- Google AI Blog (ai.googleblog.com)
- 机器之心 (jiqizhixin.com)
- 量子位 (qbitai.com)
- Paper Digest (arxiv.org)

### 游戏开发
- Unity Blog (blog.unity.com)
- Unreal Engine (unrealengine.com)
- Godot News (godotengine.org)
- Gamasutra (gamasutra.com)
- IndieDB (indiedb.com)

### 健康生活
- 丁香医生 (dxy.com)
- 健康时报 (healthtimes.cn)
- 果壳 (guokr.com)
- 生命时报 (lifetimes.cn)

---

## 自动化收集

定时任务每天 18:00 自动运行：
```bash
# 收集所有知识库
0 18 * * * cd /workspace/projects/workspace && python3 skills/content-collector/scripts/full_pipeline.py --week current
```

手动运行收集：
```bash
# 收集单个知识库
python skills/content-collector/scripts/collect.py --kb ai-latest-news --week current

# 收集所有知识库
python skills/content-collector/scripts/collect_all.py --week current
```

---

## 注意事项

1. **搜索结果依赖网络**：如果搜索失败，可能是网络问题或搜索API限制
2. **关键词质量**：使用具体的关键词可以获得更相关的结果
3. **去重机制**：相同URL的内容会被自动去重
4. **手动补充**：建议自动收集后手动检查和补充高质量内容
