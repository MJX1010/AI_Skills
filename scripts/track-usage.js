#!/usr/bin/env node
/**
 * Token 使用追踪脚本
 * 解析会话日志并累计 Token 消耗
 */

const fs = require('fs');
const path = require('path');

// 配置路径
const SESSIONS_DIR = '/workspace/projects/agents/main/sessions';
const USAGE_FILE = '/workspace/projects/workspace/memory/token-usage.json';

// 初始化数据结构
function initUsageData() {
  return {
    total: {
      inputTokens: 0,
      outputTokens: 0,
      totalTokens: 0,
      estimatedCost: 0,
      sessionCount: 0
    },
    daily: {},
    sessions: [],
    lastUpdated: new Date().toISOString()
  };
}

// 加载已有数据
function loadUsageData() {
  try {
    if (fs.existsSync(USAGE_FILE)) {
      const data = JSON.parse(fs.readFileSync(USAGE_FILE, 'utf-8'));
      return data;
    }
  } catch (e) {
    console.error('加载历史数据失败:', e.message);
  }
  return initUsageData();
}

// 保存数据
function saveUsageData(data) {
  try {
    fs.writeFileSync(USAGE_FILE, JSON.stringify(data, null, 2));
  } catch (e) {
    console.error('保存数据失败:', e.message);
  }
}

// 解析会话日志中的 token 数据
function parseSessionFile(filepath) {
  const tokens = [];
  try {
    const content = fs.readFileSync(filepath, 'utf-8');
    const lines = content.split('\n');
    
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const record = JSON.parse(line);
        // OpenClaw 会话格式：type=message 且包含 usage
        if (record.type === 'message' && record.message) {
          const msg = record.message;
          if (msg.role === 'assistant' && msg.usage) {
            tokens.push({
              timestamp: record.timestamp || msg.timestamp,
              inputTokens: msg.usage.input || msg.usage.prompt_tokens || 0,
              outputTokens: msg.usage.output || msg.usage.completion_tokens || 0,
              totalTokens: msg.usage.totalTokens || msg.usage.total_tokens || 0,
              model: msg.model || 'unknown'
            });
          }
        }
      } catch (e) {
        // 忽略解析错误的行
      }
    }
  } catch (e) {
    console.error(`解析文件失败 ${filepath}:`, e.message);
  }
  return tokens;
}

// 估算成本（基于 Kimi K2.5 价格）
function estimateCost(inputTokens, outputTokens) {
  // Kimi K2.5 参考价格（每百万 tokens）
  // 输入: ~$0.5/1M, 输出: ~$2/1M
  const inputCost = (inputTokens / 1000000) * 0.5;
  const outputCost = (outputTokens / 1000000) * 2;
  return inputCost + outputCost;
}

// 主函数
function main() {
  console.log('📊 Token 使用追踪\n');
  
  const usage = loadUsageData();
  
  // 扫描所有会话文件
  const files = fs.readdirSync(SESSIONS_DIR)
    .filter(f => f.endsWith('.jsonl') && !f.includes('.lock'))
    .map(f => ({
      name: f,
      path: path.join(SESSIONS_DIR, f),
      mtime: fs.statSync(path.join(SESSIONS_DIR, f)).mtime
    }))
    .sort((a, b) => b.mtime - a.mtime);
  
  let newSessions = 0;
  let sessionTokens = [];
  
  for (const file of files) {
    // 检查是否已处理过
    if (usage.sessions.some(s => s.file === file.name)) {
      continue;
    }
    
    const tokens = parseSessionFile(file.path);
    if (tokens.length === 0) continue;
    
    const sessionInput = tokens.reduce((sum, t) => sum + t.inputTokens, 0);
    const sessionOutput = tokens.reduce((sum, t) => sum + t.outputTokens, 0);
    const sessionTotal = tokens.reduce((sum, t) => sum + t.totalTokens, 0);
    
    const date = file.mtime.toISOString().split('T')[0];
    
    usage.sessions.push({
      file: file.name,
      date: date,
      inputTokens: sessionInput,
      outputTokens: sessionOutput,
      totalTokens: sessionTotal,
      messageCount: tokens.length,
      cost: estimateCost(sessionInput, sessionOutput)
    });
    
    // 累计到总数
    usage.total.inputTokens += sessionInput;
    usage.total.outputTokens += sessionOutput;
    usage.total.totalTokens += sessionTotal;
    usage.total.sessionCount++;
    
    // 按日期累计
    if (!usage.daily[date]) {
      usage.daily[date] = {
        inputTokens: 0,
        outputTokens: 0,
        totalTokens: 0,
        sessionCount: 0,
        cost: 0
      };
    }
    usage.daily[date].inputTokens += sessionInput;
    usage.daily[date].outputTokens += sessionOutput;
    usage.daily[date].totalTokens += sessionTotal;
    usage.daily[date].sessionCount++;
    usage.daily[date].cost += estimateCost(sessionInput, sessionOutput);
    
    newSessions++;
  }
  
  // 更新总成本
  usage.total.estimatedCost = estimateCost(
    usage.total.inputTokens,
    usage.total.outputTokens
  );
  usage.lastUpdated = new Date().toISOString();
  
  // 保存数据
  saveUsageData(usage);
  
  // 输出报告
  console.log('═══════════════════════════════════════');
  console.log('📈 累计统计');
  console.log('═══════════════════════════════════════');
  console.log(`总输入 Tokens:  ${usage.total.inputTokens.toLocaleString()}`);
  console.log(`总输出 Tokens:  ${usage.total.outputTokens.toLocaleString()}`);
  console.log(`总 Tokens:      ${usage.total.totalTokens.toLocaleString()}`);
  console.log(`会话数:         ${usage.total.sessionCount}`);
  console.log(`预估成本:       $${usage.total.estimatedCost.toFixed(4)}`);
  console.log('\n═══════════════════════════════════════');
  console.log('📅 每日统计（最近7天）');
  console.log('═══════════════════════════════════════');
  
  const sortedDates = Object.keys(usage.daily).sort().slice(-7);
  for (const date of sortedDates) {
    const d = usage.daily[date];
    console.log(`${date}: ${d.totalTokens.toLocaleString().padStart(8)} tokens | $${d.cost.toFixed(4)}`);
  }
  
  console.log('\n═══════════════════════════════════════');
  console.log('📝 最近会话');
  console.log('═══════════════════════════════════════');
  const recentSessions = usage.sessions.slice(-5);
  for (const s of recentSessions) {
    console.log(`${s.date} | ${s.totalTokens.toLocaleString().padStart(6)} tokens | ${s.messageCount} 条消息`);
  }
  
  console.log(`\n✅ 新增 ${newSessions} 个会话统计`);
  console.log(`💾 数据已保存至: ${USAGE_FILE}`);
}

if (require.main === module) {
  main();
}

module.exports = { loadUsageData, parseSessionFile };
