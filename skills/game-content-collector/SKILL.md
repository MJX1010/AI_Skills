---
name: game-content-collector
description: |
  Collect and archive game development related content from reliable sources including game forums, 
  blogs, news sites, and industry updates. Weekly collection format with link references. 
  Use when user asks about game dev news, "收集游戏资讯", "游戏开发动态", or weekly game industry updates.
---

# Game Content Collector

自动收集、整理和归档游戏开发相关的网络内容，每周发布一期周刊。

## 工作流程

### 1. 内容发现

从可靠的游戏开发来源搜索内容：
- **游戏引擎官方**：Unity、Unreal、Godot 博客
- **游戏媒体**：Gamasutra、Game Developer、IndieGames
- **开发者社区**：Reddit r/gamedev、Discord 社区
- **中文来源**：IndieNova、奶牛关、游戏葡萄

#### 推荐搜索组合

**英文搜索**：
```bash
npx ts-node skills/coze-web-search/scripts/search.ts \
  -q "game development news Unity Unreal" \
  --time-range 1w --count 10
```

**中文搜索**：
```bash
npx ts-node skills/coze-web-search/scripts/search.ts \
  -q "游戏开发 Unity 独立游戏 最新动态" \
  --time-range 1w --count 10
```

### 2. 内容分类

自动分类游戏开发内容：
- **🎮 游戏引擎** - Unity、Unreal、Godot 更新
- **🎯 游戏设计** - 设计理念、机制分析
- **💻 开发技术** - 编程、图形、AI
- **🎨 美术资源** - 美术工具、素材资源
- **🎵 音频音效** - 音频工具、音乐资源
- **📊 行业资讯** - 市场数据、公司动态
- **🏆 独立游戏** - 独立游戏发布、成功案例

### 3. 信息提取

从内容中提取：
- **标题** - 文章/资源标题
- **摘要** - 核心内容总结
- **关键要点** - 3-5 个要点
- **发布时间** - 文章日期
- **来源** - 网站/作者（必须添加链接引用）
- **标签** - 游戏类型、技术栈

### 4. 归档整理（时间层级 + 模块分类）

#### 时间层级结构

按**年/月/周/日**四层结构组织：

```
🎮 游戏开发/
├── 📅 2026年（年度索引）
│   └── 📅 3月（月度汇总）
│       └── 📅 第11周（周汇总）
│           └── 📄 3月13日（日文档）
└── 🗄️ 历史归档（超过1年）
```

#### 模块分类

| 模块 | 说明 | 关键词 |
|------|------|--------|
| **🎮 游戏引擎** | Unity、Unreal、Godot更新 | 引擎、渲染、性能优化 |
| **🎯 游戏设计** | 设计理念、机制分析 | 设计、机制、玩法、关卡 |
| **💻 开发技术** | 编程、图形、AI | 代码、算法、AI、物理 |
| **🎨 美术资源** | 美术工具、素材资源 | 美术、模型、动画、特效 |
| **🎵 音频音效** | 音频工具、音乐资源 | 音效、音乐、配音、声音 |
| **🏆 独立游戏** | 独立游戏发布、成功案例 | indie、独立游戏、发布 |

#### 归档格式

```markdown
# 🎮 游戏开发 - 2026年3月13日

> **模块**: 🎮 游戏引擎  
> **日期**: 2026年3月13日（周四）  
> **周次**: 第11周

---

### [Unity 6 发布新特性](URL)

**摘要**: Unity 6带来了全新的渲染管线和...

**来源**: [Unity Blog](URL) · 2026-03-20

**标签**: Unity, 游戏引擎, 渲染

---
```

## 内容源配置

详见 `references/sources.md` 获取完整的游戏开发资源链接。

### 主要来源

| 类型 | 来源 |
|------|------|
| **引擎官方** | Unity Blog、Unreal Engine、Godot News |
| **技术博客** | Gamasutra、Game Developer、80.lv |
| **中文社区** | IndieNova、奶牛关、游戏葡萄、机核 |
| **资源平台** | itch.io、Steam、Epic Games Store |
| **开发者社区** | Reddit r/gamedev、Discord |

## 使用方法

### 手动执行

收集本周游戏开发内容：
```bash
python /workspace/projects/workspace/skills/game-content-collector/scripts/collect_weekly.py --week current
```

### 自动执行

通过 cron 或 heartbeat 每周自动运行（推荐周五下午）：
```bash
# 每周五下午 6 点执行
0 18 * * 5 cd /workspace/projects/workspace && python skills/game-content-collector/scripts/collect_weekly.py
```

## 输出格式

### 周刊式归档

参考《科技爱好者周刊》格式：
- 标题：「游戏开发周刊：第X期（日期）」
- 结构：封面图 → 本周话题 → 分类内容 → 链接引用
- 风格：简洁、实用、有观点
- 链接：每条内容都有清晰的来源链接 `[标题](URL)`

## 自动化集成

### 添加到 HEARTBEAT.md

```markdown
### 游戏开发周刊（每周五下午 6:00）
- [ ] 运行游戏开发内容收集脚本
- [ ] 按「引擎/设计/技术/美术/音频/行业/独游」分类整理
- [ ] 添加链接引用（标题链接 + 来源标注）
- [ ] 发布新一期周刊到飞书知识库
```

## 注意事项

1. **内容质量** - 精选高质量内容，宁缺毋滥
2. **链接引用** - **必须**添加来源链接，尊重原创
3. **每周节奏** - 固定每周五发布
4. **分类清晰** - 游戏开发内容按技术领域细分

## 与 AI 内容收集的区别

| 维度 | AI内容收集 | 游戏内容收集 |
|------|------------|--------------|
| **主题** | AI/ML/LLM | 游戏开发/设计 |
| **来源** | AI研究机构、技术媒体 | 游戏引擎、开发者社区 |
| **分类** | 论文/新闻/工具 | 引擎/设计/美术/音频 |
| **受众** | AI从业者 | 游戏开发者 |
