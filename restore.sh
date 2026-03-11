#!/bin/bash
# 个性化配置一键恢复脚本
# 系统重装后运行此脚本，恢复所有个性化配置
# 用法：bash restore.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORY_DIR="/home/node/.claude/projects/-workspace-group/memory"
DATA_DIR="/workspace/group/data"

echo "🔧 恢复个性化配置..."

# 1. 恢复全局宪法
mkdir -p ~/.claude
cp "$REPO_DIR/CLAUDE.md" ~/.claude/CLAUDE.md
echo "✅ 全局宪法 → ~/.claude/CLAUDE.md"

# 2. 恢复工作记忆
mkdir -p "$MEMORY_DIR"
cp "$REPO_DIR/MEMORY.md" "$MEMORY_DIR/MEMORY.md"
echo "✅ 工作记忆 → $MEMORY_DIR/MEMORY.md"

# 3. 恢复数据脚本
mkdir -p "$DATA_DIR"
cp "$REPO_DIR/data/token_report.py" "$DATA_DIR/token_report.py"
cp "$REPO_DIR/data/container_aliases.json" "$DATA_DIR/container_aliases.json"
echo "✅ token 统计脚本 → $DATA_DIR/"

# 4. 应用 agent-runner SQLite 补丁
AGENT_RUNNER_DIR="/workspace/project/container/agent-runner"
PATCH_FILE="$REPO_DIR/patches/agent-runner-sqlite.patch"

if [ -d "$AGENT_RUNNER_DIR" ]; then
    cd "$AGENT_RUNNER_DIR"
    if patch --dry-run -p1 < "$PATCH_FILE" > /dev/null 2>&1; then
        patch -p1 < "$PATCH_FILE"
        npm run build
        echo "✅ agent-runner SQLite 补丁已应用并编译"
    else
        echo "⚠️  SQLite 补丁已应用（或已是最新版），跳过"
    fi
    cd "$REPO_DIR"
else
    echo "⚠️  未找到 agent-runner 目录，跳过 SQLite 补丁"
fi

echo ""
echo "🎉 恢复完成！"
echo ""
echo "ℹ️  定时任务需手动重建，参考 tasks.md"
echo "ℹ️  GitHub token 通过容器 secrets 注入（\$GITHUB_TOKEN），无需手动配置"
