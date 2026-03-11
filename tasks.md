# 定时任务配置备份

重装 nanoclaw 后，在小智私聊中发送以下内容重建定时任务。

---

## 全局宪法自动同步
每天 UTC 06:00（北京时间 14:00）自动同步全局宪法到 GitHub。

> 创建定时任务：每天 UTC 06:00 执行全局宪法同步
> `cd /workspace/group/nanoclaw-config && git pull origin main && bash sync_charter.sh "auto: 每日宪法同步"`

---

## 待办早报
每天北京时间 09:00 发送待办早报。

> 创建定时任务：每天09:00（北京时间）执行每日待办早报，读取 /workspace/group/data/todos.json

---

## 待办周复盘
每周日北京时间 20:00 发送本周复盘。

> 创建定时任务：每周日20:00（北京时间）执行待办周复盘，读取 /workspace/group/data/todos.json

---

## 期权投资团队（options-trading 项目）

> 以下任务在 options-trading 项目 README 有详细说明，重装后参考该项目文档重建。

| 任务 | 频率 | 说明 |
|------|------|------|
| 持仓提醒巡检 | 工作日 09:00-16:00 & 21:00-23:00 每小时 | 纯代码，零LLM |
| 美股早盘扫描 | 工作日 21:15 HKT | 调度器 |
| 港股早盘扫描 | 工作日 09:15 HKT | 调度器 |
| 周末持仓巡检 | 周六 09:00 HKT | CIO |
| 每周CFO报告 | 周一 09:00 HKT | CFO token消耗报告 |
| 每周CTO审查 | 周一 08:30 HKT | CTO技术审查 |
| 月度管理循环 | 每月1日 09:00 HKT | 月度总结 |
