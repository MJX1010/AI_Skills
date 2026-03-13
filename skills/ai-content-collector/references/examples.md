# AI 内容收集使用示例

## 示例 1: 手动收集今日内容

```bash
python scripts/collect_daily.py --date today
```

输出:
```
正在收集 2026-03-12 的 AI 内容...
  搜索: AI artificial intelligence latest news
  搜索: LLM large language model new research
  搜索: machine learning latest papers
  发现 6 个链接
  抓取: https://openai.com/blog/...
  抓取: https://arxiv.org/abs/...
  ...
✅ 已保存到: /workspace/projects/workspace/memory/ai-content/daily/ai-content-2026-03-12.md

📊 统计:
   日期: 2026-03-12
   内容数: 6
   分类: 技术博客(2), 研究论文(2), 行业动态(2)
```

## 示例 2: 收集昨天内容并保存为 JSON

```bash
python scripts/collect_daily.py --date yesterday --output json
```

## 示例 3: 限制收集数量

```bash
python scripts/collect_daily.py --limit 5
```

## 输出文档示例

```markdown
# AI 内容归档 - 2026-03-12

收集时间: 2026-03-12 09:30

共收集 6 条内容

## 📑 目录

- [技术博客](#技术博客)
- [研究论文](#研究论文)
- [行业动态](#行业动态)

---

## 技术博客

### 1. [OpenAI 发布 GPT-5 预览](https://openai.com/blog/...)

- **摘要**: OpenAI 今日发布了 GPT-5 的预览版本，展示了更强的推理能力和多模态理解...
- **来源**: openai.com

### 2. [Google DeepMind 的新突破](https://deepmind.google/blog/...)

- **摘要**: DeepMind 团队在蛋白质折叠预测方面取得了新进展...
- **来源**: deepmind.google

---

## 研究论文

### 1. [Efficient Transformers: A Survey](https://arxiv.org/abs/...)

- **摘要**: 本文全面综述了高效 Transformer 架构的最新进展...
- **来源**: arxiv.org

---

## 行业动态

### 1. [Anthropic 获得新一轮融资](https://techcrunch.com/...)

- **摘要**: Anthropic 宣布获得 7.5 亿美元融资，估值达到...
- **来源**: techcrunch.com
```

## 自动化设置

### 添加到 crontab

```bash
# 编辑 crontab
crontab -e

# 每天上午 9 点自动收集
0 9 * * * cd /workspace/projects/workspace && /usr/bin/python3 skills/ai-content-collector/scripts/collect_daily.py >> logs/ai-content.log 2>&1

# 或者每 4 小时收集一次
0 */4 * * * cd /workspace/projects/workspace && /usr/bin/python3 skills/ai-content-collector/scripts/collect_daily.py >> logs/ai-content.log 2>&1
```

### 添加到 HEARTBEAT.md

```markdown
### 4. AI 内容收集（每天）
- [ ] 运行 AI 内容收集脚本
- [ ] 检查收集质量和数量
- [ ] 重要内容更新到 MEMORY.md
```

## 飞书集成

收集完成后自动创建飞书文档:

```python
# 在 collect_daily.py 中添加
from feishu_doc import create_doc

# 生成内容后
doc_url = create_doc(
    title=f"AI内容归档-{date_str}",
    content=md_content
)
```
