---
name: openclaw-updater
description: |
  Track and monitor OpenClaw updates, including version changes, new features, 
  documentation updates, and configuration changes. Use when user asks about 
  OpenClaw updates, version checks, changelog review, or when performing 
  periodic OpenClaw maintenance.
---

# OpenClaw Updater

监控 OpenClaw 的更新情况，包括版本发布、新功能、文档变更等。

## 监控内容

### 1. 版本更新

- OpenClaw 核心版本更新
- Gateway 版本更新
- CLI 工具更新
- 插件/扩展更新

### 2. 功能发布

- 新工具支持
- 新渠道集成
- 新配置选项
- API 变更

### 3. 文档更新

- 官方文档变更
- API 文档更新
- 配置指南更新
- 示例代码更新

### 4. 安全更新

- 安全补丁
- 漏洞修复
- 配置安全建议

---

## 检查更新的方法

### 方法1：检查本地版本

```bash
# 检查 OpenClaw 版本
openclaw --version

# 检查 Gateway 状态
openclaw gateway status

# 查看已安装插件
openclaw plugins list
```

### 方法2：查看官方资源

1. **GitHub Releases**
   - 访问：https://github.com/openclaw/openclaw/releases
   - 查看最新版本和更新日志

2. **官方文档**
   - 访问：https://docs.openclaw.ai
   - 检查文档更新

3. **ClawHub Skills**
   - 访问：https://clawhub.com
   - 检查新发布的 skills

### 方法3：对比当前配置

```bash
# 查看当前配置
cat ~/.config/openclaw/config.yaml

# 对比示例配置
cat /usr/lib/node_modules/openclaw/docs/examples/config.yaml
```

---

## 更新流程

### 发现更新后

1. **评估更新重要性**
   - 🔴 高：安全修复、关键bug修复
   - 🟡 中：新功能、性能优化
   - 🟢 低：文档更新、示例更新

2. **阅读更新日志**
   - 查看 `references/sources.md` 中的官方资源
   - 了解破坏性变更
   - 检查是否需要配置更新

3. **备份当前配置**
   ```bash
   cp ~/.config/openclaw/config.yaml ~/.config/openclaw/config.yaml.backup
   ```

4. **执行更新**
   ```bash
   # 使用包管理器更新
   npm update -g openclaw
   
   # 或使用安装脚本
   curl -fsSL https://openclaw.ai/install.sh | sh
   ```

5. **验证更新**
   ```bash
   openclaw --version
   openclaw gateway status
   ```

6. **更新配置（如需要）**
   - 对比新旧配置差异
   - 迁移自定义配置
   - 测试功能是否正常

---

## 记录更新

更新后记录到 `memory/openclaw-updates.json`：

```json
{
  "lastCheck": "2026-03-13T08:00:00Z",
  "currentVersion": "1.x.x",
  "latestVersion": "1.x.x",
  "updates": [
    {
      "date": "2026-03-13",
      "version": "1.x.x",
      "type": "feature|fix|security|docs",
      "description": "更新描述",
      "actionRequired": true|false
    }
  ]
}
```

---

## 自动化检查

### 添加到 HEARTBEAT.md

```markdown
### OpenClaw 更新检查（每周）
- [ ] 运行 `openclaw-updater` skill 检查更新
- [ ] 查看最新 GitHub releases
- [ ] 检查官方文档变更
- [ ] 如有更新，评估并执行更新
- [ ] 记录更新日志
```

### 手动执行

```bash
# 运行更新检查
python /workspace/projects/workspace/skills/openclaw-updater/scripts/check_updates.py
```

---

## 参考资源

详见 `references/sources.md` 获取完整的 OpenClaw 资源链接。