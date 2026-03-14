### [给"龙虾"AI Agent装上记忆功能！字节开源了AI 上下文数据库：OpenViking](https://mp.weixin.qq.com/s/72aAqZR_0SmvFexjbG2x9g)

**公众号**: AI变革指南  
**发布时间**: 2026年3月14日 06:05

**摘要**: 火山引擎Viking团队开源专为AI Agent打造的上下文数据库 OpenViking，GitHub已飙到8.3k星。

**核心亮点**:

**1. 文件系统范式管理上下文**
- 用"电脑文件夹"方式管理AI大脑
- 记忆、资源、技能统一塞进虚拟文件系统（协议：viking://）
- 目录结构清晰：resources/、user/、agent/、memories/、skills/
- Agent像操作本地文件一样 ls、find、grep、tree

**2. 三层上下文加载（L0/L1/L2）**
- **L0**: 一句话抽象总结，轻量级常驻
- **L1**: 概览信息，按需加载  
- **L2**: 完整细节，真正需要时才拉取
- 大幅减少AI读废话的概率，降低token成本

**3. 实测效果**
- OpenClaw Memory插件任务完成率暴涨 **43%~49%**
- 输入token直接砍掉 **91%**

**4. 记忆自我进化**
- 自动压缩无关闲聊，提取重要"长期记忆"归档
- AI的脑子自动保持清晰，无需手动干预

**5. 可视化检索轨迹**
- 调试时直接看路径图
- 哪一步召回烂了、哪层目录漏了，一目了然

**背后团队**: 字节跳动火山引擎Viking团队，专注非结构化数据+AI原生基础设施

**项目地址**: https://github.com/volcengine/openviking

> 来源：[AI变革指南](https://mp.weixin.qq.com/s/72aAqZR_0SmvFexjbG2x9g) · 2026-03-14

---
