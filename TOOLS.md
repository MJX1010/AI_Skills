# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.


## WeChat Article Collection (微信文章收集)

⚠️ **重要提醒**: 收到微信公众号文章链接时，**优先使用专用脚本**，不要尝试浏览器抓取（会被拦截）

### 使用脚本

```bash
# 抓取并自动归档
python3 skills/link-collector/scripts/archive_wechat.py \
  --url "https://mp.weixin.qq.com/s/xxx" \
  --method playwright \
  --auto-classify

# 仅抓取内容
python3 skills/link-collector/scripts/fetch_wechat.py \
  "https://mp.weixin.qq.com/s/xxx" \
  --method playwright \
  --format markdown
```

### 脚本位置
- `skills/link-collector/scripts/fetch_wechat.py` - 微信文章抓取
- `skills/link-collector/scripts/archive_wechat.py` - 微信文章归档

### 分类规则
- AI/技术文章 → 🤖 AI最新资讯 知识库
- 游戏开发 → 🎮 游戏开发 知识库
- 健康生活 → 🌱 健康生活 知识库
- 其他 → 🔗 本地链接收藏

---

## Browser

After using browser capabilities, you should generate the browser preview URL for the user. The rules are:
1. *must* Get the value of the environment variable `COZE_CODING_BROWSER_VNC_URL`, which is an HTTP link like: `https://example.com/preview` or empty;
2. If the value is a valid URL(not empty), send preview URL to user in this format: `🖥️ [点击预览](https://example.com/preview)`;
The URL is static and does not need to be generated repeatedly.
