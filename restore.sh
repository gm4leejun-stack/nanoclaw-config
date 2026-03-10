#!/bin/bash
# Andy 全局配置恢复脚本
# 系统重装后运行此脚本，恢复 Andy 的全局宪法和工作记忆
# 用法：bash restore.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORY_DIR="/home/node/.claude/projects/-workspace-group/memory"

echo "🔧 恢复 Andy 全局配置..."

# 1. 恢复全局宪法
mkdir -p ~/.claude
cp "$REPO_DIR/CLAUDE.md" ~/.claude/CLAUDE.md
echo "✅ 全局宪法已恢复 → ~/.claude/CLAUDE.md"

# 2. 恢复工作记忆
mkdir -p "$MEMORY_DIR"
cp "$REPO_DIR/MEMORY.md" "$MEMORY_DIR/MEMORY.md"
echo "✅ 工作记忆已恢复 → $MEMORY_DIR/MEMORY.md"

echo ""
echo "🎉 恢复完成！"
echo ""
echo "⚠️  还需要做一件事："
echo "   告诉 Andy：「这是我的 GitHub token：ghp_xxx」"
echo "   Andy 会自动保存到 MEMORY.md，后续 git push 全自动"
