#!/usr/bin/env node
/**
 * 飞书工具调用 wrapper
 * 用法: node feishu-tool.js <tool> <action> [args...]
 */

const { execSync } = require('child_process');
const path = require('path');

const OPENCLAW_PATH = '/usr/lib/node_modules/openclaw';

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('用法: node feishu-tool.js <tool> <action> [args...]');
    process.exit(1);
  }

  const [tool, action, ...restArgs] = args;
  
  // 构建参数对象
  const params = { action };
  for (let i = 0; i < restArgs.length; i += 2) {
    const key = restArgs[i].replace(/^--/, '');
    const value = restArgs[i + 1];
    if (key && value !== undefined) {
      params[key] = value;
    }
  }

  try {
    // 动态加载工具模块
    const toolPath = path.join(OPENCLAW_PATH, 'dist/plugin-sdk/feishu.js');
    const feishuModule = require(toolPath);
    
    const toolFn = feishuModule[`feishu_${tool}`];
    if (!toolFn) {
      console.error(`未知工具: ${tool}`);
      process.exit(1);
    }

    const result = await toolFn(params);
    console.log(JSON.stringify(result));
  } catch (error) {
    console.error(JSON.stringify({ error: error.message }));
    process.exit(1);
  }
}

main();
