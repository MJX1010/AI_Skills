### [Mac 本地安装原生 OpenClaw 补充说明](https://mp.weixin.qq.com/s/yqNRNerMFJefadcl7oe-lA)

**公众号**: OpenClaw 用户分享
**发布时间**: 2026年3月14日 11:22

**摘要**: Mac 系统本身就是 Unix 和 FreeBSD 演化而来，很适合当服务器用，养虾最合适。

**关键要点**:
1. **安全防护** - 使用 OpenClaw 和 Agent 时一定要注意安全和防护
2. **版本升级** - 使用 `npm i -g openclaw@latest` 升级到最新版本 (v2026.3.11)
3. **模型选择** - 推荐使用国产大模型（MiniMax M2.5 等），更便宜，避免使用 Gemini API（易封号）
4. **MiniMax MCP 工具** - 安装 Coding Plan MCP 实现图片识别和精确搜索能力：
   - 安装 mcporter: `npm install -g mcporter`
   - 安装 uvx: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - 配置 MCP Server 即可使用 `web_search` 和 `understand_image` 工具

> 来源：[微信公众号](https://mp.weixin.qq.com/s/yqNRNerMFJefadcl7oe-lA) · 2026-03-14

---
