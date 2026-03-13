---
name: health-content-collector
description: |
  Collect and archive health and wellness related content including fitness, nutrition, 
  mental health, and lifestyle tips. Weekly collection format with link references.
  Use when user asks about health news, "健康知识", "生活妙招", or weekly wellness updates.
---

# Health Content Collector

自动收集、整理和归档健康生活相关的网络内容，每周发布一期周刊。

## 工作流程

### 1. 内容发现

从可靠的健康生活来源搜索内容：
- **健康科普**：丁香医生、健康界、39健康网
- **运动健身**：Keep、薄荷健康、健身类公众号
- **心理健康**：心理学科普、压力管理、睡眠改善
- **生活妙招**：知乎生活技巧、生活小窍门

#### 推荐搜索组合

**中文搜索**：
```bash
npx ts-node skills/coze-web-search/scripts/search.ts \
  -q "健康知识 生活妙招 运动健身" \
  --time-range 1w --count 10
```

### 2. 内容分类

自动分类健康生活内容：
- **🏃 运动健身** - 锻炼方法、健身计划、运动科普
- **🥗 饮食营养** - 健康饮食、营养搭配、食谱推荐
- **😊 心理健康** - 压力管理、情绪调节、睡眠改善
- **💤 睡眠健康** - 睡眠质量、作息规律、失眠改善
- **🏥 医疗资讯** - 疾病预防、健康检查、医学科普
- **✨ 生活妙招** - 生活技巧、小窍门、实用方法

### 3. 信息提取

从内容中提取：
- **标题** - 文章/资源标题
- **摘要** - 核心内容总结
- **关键要点** - 3-5 个要点
- **发布时间** - 文章日期
- **来源** - 网站/作者（必须添加链接引用）
- **标签** - 健康分类

### 4. 归档整理（时间层级 + 模块分类）

#### 时间层级结构

按**年/月/周/日**四层结构组织：

```
🌱 健康生活/
├── 📅 2026年（年度索引）
│   └── 📅 3月（月度汇总）
│       └── 📅 第11周（周汇总）
│           └── 📄 3月13日（日文档）
└── 🗄️ 历史归档（超过1年）
```

#### 模块分类

| 模块 | 说明 | 关键词 |
|------|------|--------|
| **🏃 运动健身** | 锻炼方法、健身计划、运动科普 | 运动、健身、跑步、瑜伽 |
| **🥗 饮食营养** | 健康饮食、营养搭配、食谱推荐 | 饮食、营养、食谱、减肥 |
| **😊 心理健康** | 压力管理、情绪调节、睡眠改善 | 心理、压力、情绪、冥想 |
| **💤 睡眠健康** | 睡眠质量、作息规律、失眠改善 | 睡眠、失眠、作息、熬夜 |
| **🏥 医疗资讯** | 疾病预防、健康检查、医学科普 | 疾病、医疗、预防、检查 |
| **✨ 生活妙招** | 生活技巧、小窍门、实用方法 | 生活、窍门、技巧、妙招 |

#### 归档格式

```markdown
# 🌱 健康生活 - 2026年3月13日

> **模块**: 🏃 运动健身  
> **日期**: 2026年3月13日（周四）  
> **周次**: 第11周

---

### [30天健身计划：从入门到进阶](URL)

**摘要**: 科学的健身计划帮助你...

**来源**: [Keep](URL) · 2026-03-13

**标签**: 运动、健身、计划

---
```

## 内容源配置

详见 `references/sources.md` 获取完整的健康生活资源链接。

### 主要来源

| 类型 | 来源 |
|------|------|
| **健康科普** | 丁香医生、健康界、39健康网 |
| **运动健身** | Keep、薄荷健康、健身公众号 |
| **心理健康** | 壹心理、简单心理、心理学科普 |
| **生活技巧** | 知乎生活、小红书、什么值得买 |
| **营养饮食** | 营养师顾中一、范志红营养师 |

## 使用方法

### 手动执行

收集本周健康生活内容：
```bash
python /workspace/projects/workspace/skills/health-content-collector/scripts/collect_weekly.py --week current
```

### 自动执行

通过 cron 或 heartbeat 每周自动运行（推荐周五下午）：
```bash
# 每周五下午 6 点执行
0 18 * * 5 cd /workspace/projects/workspace && python skills/health-content-collector/scripts/collect_weekly.py
```

## 输出格式

### 周刊式归档

参考《科技爱好者周刊》格式：
- 标题：「健康生活周刊：第X期（日期）」
- 结构：封面图 → 本周话题 → 分类内容 → 链接引用
- 风格：简洁、实用、有观点
- 链接：每条内容都有清晰的来源链接 `[标题](URL)`

## 自动化集成

### 添加到 HEARTBEAT.md

```markdown
### 健康生活周刊（每周五下午 6:00）
- [ ] 运行健康生活内容收集脚本
- [ ] 按「运动/饮食/心理/睡眠/医疗/妙招」分类整理
- [ ] 添加链接引用（标题链接 + 来源标注）
- [ ] 发布新一期健康生活周刊到飞书知识库
```

## 完整工作流：收集 → 分类 → 归档 → 同步

### 步骤1：内容收集

运行周刊收集脚本，获取本周健康生活相关内容：
```bash
python /workspace/projects/workspace/skills/health-content-collector/scripts/collect_weekly.py --week current
```

收集结果保存在：
- `memory/health-content/weekly/health-weekly-YYYY-WXX.md`

### 步骤2：内容分类

自动按六模块分类：
- **🏃 运动健身** - 锻炼方法、健身计划、运动科普
- **🥗 饮食营养** - 健康饮食、营养搭配、食谱推荐
- **😊 心理健康** - 压力管理、情绪调节、睡眠改善
- **💤 睡眠健康** - 睡眠质量、作息规律、失眠改善
- **🏥 医疗资讯** - 疾病预防、健康检查、医学科普
- **✨ 生活妙招** - 生活技巧、小窍门、实用方法

分类逻辑：
```python
if "运动" in title or "健身" in title or "跑步" in title or "瑜伽" in title:
    module = "🏃 运动健身"
elif "饮食" in title or "营养" in title or "食谱" in title or "减肥" in title:
    module = "🥗 饮食营养"
elif "心理" in title or "压力" in title or "情绪" in title or "冥想" in title:
    module = "😊 心理健康"
elif "睡眠" in title or "失眠" in title or "作息" in title or "熬夜" in title:
    module = "💤 睡眠健康"
elif "疾病" in title or "医疗" in title or "预防" in title or "检查" in title:
    module = "🏥 医疗资讯"
elif "生活" in title or "窍门" in title or "技巧" in title or "妙招" in title:
    module = "✨ 生活妙招"
```

### 步骤3：生成本地周刊

按以下格式生成本地 Markdown：
```markdown
# 健康生活周刊：第X期（YYYY年MM月DD日）

## 📌 本周话题
（人工编辑补充）

## 🏃 运动健身
### 1. [标题](URL)
内容摘要...
> 来源：[网站名](URL)

## 🥗 饮食营养
...

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

# 获取 健康生活 知识库节点
feishu_wiki --action nodes --space_id 7616737910330510558
```

#### 4.2 创建周刊文档
在「健康生活」知识库下创建新文档：
```bash
feishu_wiki --action create \
  --space_id 7616737910330510558 \
  --parent_node_token <首页节点Token> \
  --title "第X期 - YYYY年MM月DD日" \
  --obj_type docx
```

#### 4.3 写入周刊内容
使用生成的 `obj_token` 写入 Markdown 内容：
```bash
feishu_doc --action write \
  --doc_token <obj_token> \
  --content "# 健康生活周刊..."
```

### 步骤5：更新操作日志

在 `memory/YYYY-MM-DD.md` 记录同步操作：
```markdown
## 飞书知识库同步
时间：YYYY-MM-DD HH:MM

将第X期（YYYY年MM月DD日）的健康生活周刊同步到飞书知识库：

### 🌱 健康生活
- 文档标题：第X期 - YYYY年MM月DD日
- Wiki节点：[查看文档](https://xxx.feishu.cn/wiki/xxx)
- 内容：XX条健康生活相关内容

### 本地备份文件
- `memory/health-content/weekly/health-weekly-YYYY-WXX.md`

### ⚠️ 注意事项
医疗相关内容建议专业审核
```

### 完整命令示例

```bash
# 1. 收集内容
python skills/health-content-collector/scripts/collect_weekly.py --week current

# 2. 同步到飞书（使用 obj_token）
feishu_doc --action write \
  --doc_token LyOId8qKHoPlBtxxuWuccqX1nBh \
  --content "$(cat memory/health-content/weekly/health-weekly-2026-W11.md)"
```

## 注意事项

1. **内容质量** - 精选高质量内容，宁缺毋滥
2. **科学准确** - 健康内容需确保科学性和准确性
3. **链接引用** - **必须**添加来源链接，尊重原创
4. **每周节奏** - 固定每周五发布
5. **专业审核** - 医疗相关内容建议专业审核

## 与其他周刊的区别

| 维度 | AI每周精选 | 游戏开发周刊 | 健康生活周刊 |
|------|------------|--------------|--------------|
| **主题** | AI/ML/LLM | 游戏开发 | 健康/生活/健身 |
| **来源** | AI研究机构 | 游戏引擎/社区 | 健康科普/生活平台 |
| **分类** | 论文/新闻/工具 | 引擎/设计/技术 | 运动/饮食/心理/医疗 |
| **受众** | AI从业者 | 游戏开发者 | 关注健康生活的人群 |
