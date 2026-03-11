#!/bin/bash
# 全局宪法同步脚本
# 修改 ~/.claude/CLAUDE.md 后执行此脚本，推送到 GitHub 持久化
# 用法：bash sync_charter.sh ["修改说明"]

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
MSG="${1:-sync: 全局宪法更新}"

cd "$REPO_DIR"

# ── Step 1: 先拉取 remote 最新版，确保不覆盖他人改动 ──────────────
git fetch origin main

LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)

if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
    # remote 有本地没有的 commit，先 pull --ff-only（只允许快进合并）
    echo "⚠️  remote 有新 commit，先同步..."
    git pull --ff-only origin main || {
        echo "❌ 无法快进合并（remote 与本地有分叉）。请手动 git pull 解决冲突后再运行本脚本。"
        exit 1
    }
fi

# ── Step 2: 将 ~/.claude/CLAUDE.md 同步到仓库 ──────────────────────
cp ~/.claude/CLAUDE.md "$REPO_DIR/CLAUDE.md"

# ── Step 3: 检查是否有变更 ─────────────────────────────────────────
if git diff --quiet CLAUDE.md; then
    echo "✅ 宪法无变更，无需推送"
    exit 0
fi

git add CLAUDE.md
git commit -m "$MSG"
git push origin main

echo "✅ 全局宪法已同步到 GitHub：$MSG"
