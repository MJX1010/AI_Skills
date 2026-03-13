#!/usr/bin/env node
/**
 * 快速查看 Token 使用统计
 */

const fs = require('fs');
const USAGE_FILE = '/workspace/projects/workspace/memory/token-usage.json';

function formatNumber(num) {
  return num.toLocaleString();
}

function main() {
  if (!fs.existsSync(USAGE_FILE)) {
    console.log('❌ 暂无统计数据，请先运行: node scripts/track-usage.js');
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(USAGE_FILE, 'utf-8'));
  
  console.log('╔══════════════════════════════════════════════════╗');
  console.log('║           📊 Token 使用统计总览                  ║');
  console.log('╚══════════════════════════════════════════════════╝');
  console.log();
  
  // 累计统计
  console.log('📈 累计消耗');
  console.log('────────────────────────────────────────────────────');
  console.log(`  输入 Tokens:  ${formatNumber(data.total.inputTokens).padStart(12)}`);
  console.log(`  输出 Tokens:  ${formatNumber(data.total.outputTokens).padStart(12)}`);
  console.log(`  总 Tokens:    ${formatNumber(data.total.totalTokens).padStart(12)}`);
  console.log(`  会话数量:     ${formatNumber(data.total.sessionCount).padStart(12)}`);
  console.log(`  预估成本:     $${data.total.estimatedCost.toFixed(4).padStart(10)}`);
  console.log();
  
  // 每日统计
  const sortedDates = Object.keys(data.daily).sort().slice(-7);
  if (sortedDates.length > 0) {
    console.log('📅 最近7天统计');
    console.log('────────────────────────────────────────────────────');
    console.log('  日期          Tokens        会话    预估成本');
    console.log('  ─────────────────────────────────────────────────');
    for (const date of sortedDates) {
      const d = data.daily[date];
      console.log(`  ${date}  ${formatNumber(d.totalTokens).padStart(10)}  ${d.sessionCount.toString().padStart(6)}    $${d.cost.toFixed(4)}`);
    }
    console.log();
  }
  
  // 最近会话
  console.log('📝 最近会话');
  console.log('────────────────────────────────────────────────────');
  const recent = data.sessions.slice(-5).reverse();
  for (const s of recent) {
    console.log(`  ${s.date} | ${formatNumber(s.totalTokens).padStart(8)} tokens | ${s.messageCount} 条消息`);
  }
  console.log();
  
  console.log(`💾 数据更新时间: ${new Date(data.lastUpdated).toLocaleString('zh-CN')}`);
  console.log();
  console.log('提示: 运行 node scripts/track-usage.js 更新统计');
}

main();
