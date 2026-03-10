# 工作记忆

## 工作守则（最高优先级）

两层宪法体系（均自动加载，任何 Agent 均可修改但须注明）：
- *全局宪法*（最高）→ `~/.claude/CLAUDE.md`：适用所有 nanoclaw agent
- *项目宪法*（扩展）→ `/workspace/group/options-trading/rules/team_charter.md`：期权投资专项

修改时用语：
- "修改全局宪法" → 改 `~/.claude/CLAUDE.md`
- "修改项目宪法" → 改 `team_charter.md`

## 当前进行项目
- 路径：/workspace/group/options-trading/
- 项目：AI 股票期权投资团队系统
- 状态：已上线运行

## 项目文档
- requirements.md — 需求文档
- team-design.md — 团队方案
- architecture.md — 架构方案 v3.0（最终版）
- architecture-review.md — 架构评审记录

## 已确认决策
- 团队9个角色（见 team-design.md）
- 架构：Lean CLI + nanoclaw schedule_task（无daemon进程）
- 数据库：SQLite WAL模式
- 模型分级：关键决策（研究员/策略师/风控官/复盘官/培训师）全部Sonnet，统计汇总（CHO/CFO）Haiku，记录员无LLM
- 部署：Mac mini本地，nanoclaw/openclaw同机

## 当前状态
- Phase 1+2+3 + 闭环修复全部完成，已推送 GitHub
- 最新 commit：7cede52
- 系统已上线：48只股票池，7个持仓，富途已连通，定时任务运行中

## Phase 2 完成内容（34个文件）
- data/db.py：新增 settings 表 + get_setting/set_setting
- tools/market_data.py：is_hk_stock() + 港股期权优雅降级
- agents/researcher.py：研究员（Haiku），技术+期权→JSON
- agents/strategist.py：策略师（Sonnet），具体策略参数
- agents/risk_manager.py：风控官（Haiku），独立审核+纯代码预检
- agents/pipeline.py：三级流水线协调器
- cli.py：analyze/scan/capital/recommend 新命令
- setup.sh：Futu OpenD macOS 自动检测/启动/安装
- .gitignore + git init（commit done，remote = gm4leejun-stack/options-trading）
- nanoclaw 3个定时任务：每日9:30扫描/每15分预警/每周一CFO报告

## 用户确认需求
- 股票池：对话增删，空池时引导
- 资金：cli capital set/get，未设则引导
- GitHub：gm4leejun-stack/options-trading ✅ 已推送
- 富途：setup.sh自动检测，无则引导安装
- 时区：默认北京时间UTC+8
- 港股期权：富途已连通，实时行情+期权链已实现
- 容器与Mac mini同机，FUTU_HOST=host.docker.internal

## 下一步
- Phase 4：积累真实交易数据后（回测/可视化/多腿策略）
- Phase 3D 已内置于 CFO，运行后自动触发

## 持仓注意
- 所有 PUT 仓位均为 Sell Put（卖出），非 Long Put
- QQQM 245 / NVDA 167.5 Short Put 均为260320到期（10天）
- 03690 Short Put 95 为260330到期（20天，深度实值）
