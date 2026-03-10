# nanoclaw-config

Andy 的全局配置备份。包含全局工作宪法和工作记忆，系统重装后一键恢复。

## 文件说明

| 文件 | 恢复位置 | 说明 |
|---|---|---|
| `CLAUDE.md` | `~/.claude/CLAUDE.md` | 全局宪法，所有 nanoclaw agent 自动继承 |
| `MEMORY.md` | `~/.claude/projects/-workspace-group/memory/MEMORY.md` | Andy 工作记忆 |
| `restore.sh` | — | 一键恢复脚本 |

## 系统重装后恢复步骤

```bash
git clone https://github.com/gm4leejun-stack/nanoclaw-config.git
cd nanoclaw-config
bash restore.sh
```

然后告诉 Andy：「这是我的 GitHub token：ghp_xxx」，Andy 自动保存，后续全自动。

## 修改全局宪法

任何 agent 发现宪法需要更新时：

1. 明确告知用户「修改全局宪法：[修改内容]」
2. 编辑 `~/.claude/CLAUDE.md`（立即生效）
3. 同步到此仓库并推送（持久备份）

一处修改，所有 nanoclaw agent 自动继承。
