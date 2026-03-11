import json, os, sqlite3, unicodedata
from datetime import datetime, timezone, timedelta

tz_beijing = timezone(timedelta(hours=8))
now = datetime.now(tz_beijing)
today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
week_start  = today_start - timedelta(days=today_start.weekday())
month_start = today_start - timedelta(days=29)

import unicodedata
def dw(s): return sum(2 if unicodedata.east_asian_width(c) in ('W','F') else 1 for c in s)
def rpad(s, w): return s + ' ' * max(0, w - dw(s))
def lpad(s, w): return ' ' * max(0, w - dw(s)) + s

# ── 容器显示名映射 ─────────────────────────────────────────────────
ALIASES_FILE = os.path.join(os.path.dirname(__file__), "container_aliases.json")
try:
    display_map = {k: v for k, v in json.load(open(ALIASES_FILE)).items()
                   if not k.startswith("_")}
except:
    display_map = {}

def display_name(c):
    return display_map.get(c, c.replace("telegram_", "").replace("_", "-"))

# ── SQLite 表结构（兼容旧列名）────────────────────────────────────
db_path = "/workspace/shared/usage/usage.db"

def ensure_db():
    con = sqlite3.connect(db_path)
    cols = [r[1] for r in con.execute("PRAGMA table_info(usage)").fetchall()]
    if not cols:
        con.execute("""CREATE TABLE usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL, container TEXT NOT NULL,
            input_tokens INTEGER NOT NULL, output_tokens INTEGER NOT NULL
        )""")
        con.execute("CREATE INDEX idx_ts ON usage(ts)")
        con.execute("CREATE INDEX idx_container ON usage(container)")
        con.commit()
    elif "input" in cols and "input_tokens" not in cols:
        con.execute("ALTER TABLE usage RENAME COLUMN input  TO input_tokens")
        con.execute("ALTER TABLE usage RENAME COLUMN output TO output_tokens")
        con.commit()
    con.close()

ensure_db()

# ── 查询 ───────────────────────────────────────────────────────────
def query_period(since_ts):
    con = sqlite3.connect(db_path)
    rows = con.execute("""
        SELECT container, SUM(input_tokens), SUM(output_tokens), COUNT(*)
        FROM usage WHERE ts >= ? GROUP BY container
    """, (since_ts.isoformat(),)).fetchall()
    con.close()
    return {r[0]: (r[1], r[2], r[3]) for r in rows}

data_today = query_period(today_start)
data_week  = query_period(week_start)
data_month = query_period(month_start)

def psum(d):
    return sum(v[0] for v in d.values()), sum(v[1] for v in d.values()), sum(v[2] for v in d.values())

gi,go,gq = psum(data_today)
wi,wo,wq = psum(data_week)
mi,mo,mq = psum(data_month)

def M(n): return f"{n/1e6:.3f}M"
def usd(i,o): return i*3/1e6 + o*15/1e6

# ── 动态宽度代码块生成器 ───────────────────────────────────────────
SEP = object()  # 分隔符标记

def fmt_rows(rows, widths):
    """将 rows 格式化为已对齐的字符串列表（不含 ``` 包裹）"""
    col_count = len(widths)
    lines = []
    for row in rows:
        parts = [rpad(str(row[0]), widths[0])]
        for i in range(1, col_count):
            cell = str(row[i]) if i < len(row) else ''
            parts.append(lpad(cell, widths[i]))
        lines.append(' | '.join(parts))
    return lines

def calc_widths(*row_lists):
    """跨多个 row_lists 统一计算每列最大宽度"""
    all_rows = [r for lst in row_lists for r in lst]
    col_count = max(len(r) for r in all_rows)
    widths = [0] * col_count
    for row in all_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], dw(str(cell)))
    return widths

# ── 组装输出 ───────────────────────────────────────────────────────
ip = mi/max(mi+mo,1)*100
ic = mi*3/1e6; oc = mo*15/1e6

period_rows = [
    ('今日',   M(gi+go), f'${usd(gi,go):.2f}', f'{gq}次'),
    ('本周',   M(wi+wo), f'${usd(wi,wo):.2f}', f'{wq}次'),
    ('近30天', M(mi+mo), f'${usd(mi,mo):.2f}', f'{mq}次'),
]
io_rows = [
    ('输入', M(mi), f'${ic:.2f}', f'{ip:.0f}%'),
    ('输出', M(mo), f'${oc:.2f}', f'{100-ip:.0f}%'),
]
group_rows = []
for container, (ti, to, q) in sorted(data_month.items(), key=lambda x: -(x[1][0]+x[1][1])):
    pct = (ti+to)/max(mi+mo,1)*100
    group_rows.append((display_name(container), M(ti+to), f'{pct:.0f}%', f'{q}次'))
group_rows.append(('总计', M(mi+mo), f'${usd(mi,mo):.2f}', f'{mq}次'))

widths = calc_widths(period_rows, io_rows, group_rows)
sep = '-' * (sum(widths) + 3 * (len(widths) - 1))

body = []
body.append('⏱ 时段统计')
body += fmt_rows(period_rows, widths)
body.append(sep)
body.append('📤 输入/输出 近30天')
body += fmt_rows(io_rows, widths)
body.append(sep)
body.append('🤖 各群组 近30天')
body += fmt_rows(group_rows, widths)

print(f"📊 *Token 消耗报告*  {now.strftime('%m/%d %H:%M')} (UTC+8)\n")
print("```")
print("\n".join(body))
print("```")
