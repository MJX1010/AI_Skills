# OpenClaw 资源链接

## 官方资源

### 核心仓库

| 资源 | URL | 说明 |
|------|-----|------|
| GitHub 主仓库 | https://github.com/openclaw/openclaw | 源代码 |
| GitHub Releases | https://github.com/openclaw/openclaw/releases | 版本发布 |
| 官方文档 | https://docs.openclaw.ai | 完整文档 |
| 文档镜像 | /usr/lib/node_modules/openclaw/docs | 本地文档 |

### 社区与生态

| 资源 | URL | 说明 |
|------|-----|------|
| ClawHub Skills | https://clawhub.com | Skills 市场 |
| Discord 社区 | https://discord.com/invite/clawd | 官方社区 |
| GitHub Discussions | https://github.com/openclaw/openclaw/discussions | 技术讨论 |

---

## 版本检查

### 当前版本获取

```bash
# CLI 版本
openclaw --version

# Gateway 版本
openclaw gateway status

# 包管理器版本
npm list -g openclaw
```

### 最新版本获取

```bash
# 通过 GitHub API
curl -s https://api.github.com/repos/openclaw/openclaw/releases/latest | grep tag_name

# 通过 npm
npm view openclaw version
```

---

## 更新日志跟踪

### 主要版本变更

| 版本 | 发布日期 | 主要变更 |
|------|----------|----------|
| - | - | 待记录 |

### 跟踪方法

1. **订阅 GitHub Releases**
   - 访问仓库页面
   - 点击 "Watch" → "Custom" → 勾选 "Releases"

2. **RSS 订阅**
   - Releases RSS: `https://github.com/openclaw/openclaw/releases.atom`

3. **定期检查**
   - 每周日检查一次
   - 对比当前版本与最新版本

---

## 文档资源

### 本地文档

```
/usr/lib/node_modules/openclaw/docs/
├── README.md
├── CONFIG.md
├── TOOLS.md
├── CHANNELS.md
├── GATEWAY.md
└── examples/
    └── config.yaml
```

### 关键文档页面

| 文档 | 路径 | 说明 |
|------|------|------|
| 配置指南 | docs/CONFIG.md | 完整配置参考 |
| 工具说明 | docs/TOOLS.md | 内置工具文档 |
| 渠道配置 | docs/CHANNELS.md | 消息渠道配置 |
| Gateway 指南 | docs/GATEWAY.md | Gateway 使用 |

---

## Skills 相关

### Skills 仓库

| 位置 | 路径 | 说明 |
|------|------|------|
| 系统 Skills | /usr/lib/node_modules/openclaw/skills/ | 内置 skills |
| 用户 Skills | /workspace/projects/workspace/skills/ | 自定义 skills |
| Skills 市场 | https://clawhub.com | 社区 skills |

### Skills 更新检查

```bash
# 检查本地 skills
ls -la /workspace/projects/workspace/skills/

# 对比 ClawHub 上的新 skills
# 访问 https://clawhub.com 查看最新发布
```

---

## 配置参考

### 配置文件位置

```bash
# 用户配置
~/.config/openclaw/config.yaml

# 示例配置
/usr/lib/node_modules/openclaw/docs/examples/config.yaml

# 工作区配置
/workspace/projects/workspace/openclaw-config.yaml
```

### 关键配置项

| 配置项 | 说明 | 文档链接 |
|--------|------|----------|
| channels | 消息渠道配置 | docs/CHANNELS.md |
| gateway | Gateway 配置 | docs/GATEWAY.md |
| skills | Skills 配置 | docs/SKILLS.md |
| storage | 存储配置 | docs/STORAGE.md |

---

## 更新通知设置

### 推荐跟踪方式

1. **GitHub Releases**（推荐）
   - 最权威的版本信息
   - 包含完整的更新日志
   - 提供下载链接

2. **Discord 公告频道**
   - 实时更新通知
   - 社区讨论
   - 问题反馈

3. **定期检查**（自动化）
   - 每周日自动检查
   - 记录到 `memory/openclaw-updates.json`
   - 必要时通知用户

### 检查清单

```markdown
- [ ] 检查 GitHub Releases 页面
- [ ] 查看最新版本号
- [ ] 阅读 Release Notes
- [ ] 检查是否有安全更新
- [ ] 检查是否有破坏性变更
- [ ] 检查是否需要配置更新
- [ ] 备份当前配置
- [ ] 执行更新
- [ ] 验证更新结果
- [ ] 记录更新日志
```