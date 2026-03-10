#!/bin/bash
# 全局宪法同步脚本
# 修改 ~/.claude/CLAUDE.md 后执行此脚本，推送到 GitHub 持久化
# 用法：bash sync_charter.sh ["修改说明"]

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
MSG="${1:-sync: 全局宪法更新}"

# 同步本地宪法到仓库
cp ~/.claude/CLAUDE.md "$REPO_DIR/CLAUDE.md"

cd "$REPO_DIR"

# 检查是否有变更
if git diff --quiet CLAUDE.md; then
    echo "✅ 宪法无变更，无需推送"
    exit 0
fi

git add CLAUDE.md
git commit -m "$MSG"
git push

echo "✅ 全局宪法已同步到 GitHub：$MSG"
