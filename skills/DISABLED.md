# 已禁用的 Skills

> 以下 skills 已被移至 `disabled/` 目录，避免对自定义流程产生干扰

## 禁用时间
2026-03-24

## 禁用原因
避免 coze-coding-dev-sdk 相关工具与自定义流程产生冲突或干扰

## 禁用列表

| Skill | 功能 | 禁用前路径 |
|-------|------|-----------|
| coze-image-gen | 图片生成 | `skills/coze-image-gen/` |
| coze-voice-gen | TTS/ASR 语音 | `skills/coze-voice-gen/` |
| coze-web-fetch | 网页内容抓取 | `skills/coze-web-fetch/` |
| coze-web-search | 网络搜索 | `skills/coze-web-search/` |

## 替代方案

| 原功能 | 替代方案 |
|--------|---------|
| 图片生成 | 使用外部工具或 API |
| 语音合成 | 使用系统 TTS 或其他服务 |
| 网页抓取 | 使用 `browser` 工具或自定义脚本 |
| 网络搜索 | 使用 `browser` 工具配合搜索引擎 |

## 恢复使用

如需恢复某个 skill，执行：
```bash
cd /workspace/projects/workspace/skills
mv disabled/coze-xxx ./
```

---
*禁用记录由系统自动生成*
