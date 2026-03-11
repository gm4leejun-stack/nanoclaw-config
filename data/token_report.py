import json, os, sqlite3, unicodedata
from datetime import datetime, timezone, timedelta

tz_beijing = timezone(timedelta(hours=8))
now = datetime.now(tz_beijing)
today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
week_start  = today_start - timedelta(days=today_start.weekday())
month_start = today_start - timedelta(days=29)

# ── 显示宽度工具（CJK字符=2，其他=1）─────────────────────────────
def dw(s):
    return sum(2 if unicodedata.east_asian_width(c) in ('W','F') else 1 for c in s)

def trunc(s, w):
    out, cur = '', 0
    for c in s:
        cw = 2 if unicodedata.east_asian_width(c) in ('W','F') else 1
        if cur + cw > w: return out + '…'
        out += c; cur += cw
    return out

def rpad(s, w): return s + ' ' * max(0, w - dw(s))
def lpad(s, w): return ' ' * max(0, w - dw(s)) + s

# ── 容器显示名映射 ─────────────────────────────────────────────────
ALIASES_FILE = os.path.join(os.path.dirname(__file__), "container_aliases.json")
try:
    display_map = {k: v for k, v in json.load(open(ALIASES_FILE)).items()
                   if not k.startswith("_")}
except:
    display_map = {}

def display_name(container):
    if container in display_map:
        return display_map[container]
    return container.replace("telegram_", "").replace("_", "-")

# ── 确保 SQLite 表结构（兼容旧列名迁移）───────────────────────────
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

# ── 查询统计 ───────────────────────────────────────────────────────
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

def psum(data):
    i = sum(v[0] for v in data.values())
    o = sum(v[1] for v in data.values())
    q = sum(v[2] for v in data.values())
    return i, o, q

gi,go,gq = psum(data_today)
wi,wo,wq = psum(data_week)
mi,mo,mq = psum(data_month)

# ── 卡片格式化 ─────────────────────────────────────────────────────
def M(n): return f"{n/1e6:.3f}M"
def usd(i,o): return i*3/1e6 + o*15/1e6

L, T, C, N = 9, 8, 7, 4   # 列宽: name, total, cost, count
IW = L + T + C + N + 1     # 内容宽度=29

def border(l='├', r='┤'):
    return l + '─' * IW + r

def data_row(label, total, cost, cnt):
    inner = rpad(trunc(label,L),L) + lpad(total,T) + lpad(cost,C) + lpad(cnt,N) + ' '
    return '│' + inner + '│'

def mid_divider(text):
    pad = (IW - dw(text)) // 2
    return '├' + '─'*pad + text + '─'*(IW - pad - dw(text)) + '┤'

lines = []
title = f" Token  {now.strftime('%m/%d  %H:%M')}"
lines.append(border('┌','┐'))
lines.append('│' + rpad(title, IW) + '│')
lines.append(border())
lines.append(data_row('', '总量', '费用', '次'))
lines.append(border())
lines.append(data_row('今日',   M(gi+go), f'${usd(gi,go):.2f}', str(gq)))
lines.append(data_row('本周',   M(wi+wo), f'${usd(wi,wo):.2f}', str(wq)))
lines.append(data_row('近30天', M(mi+mo), f'${usd(mi,mo):.2f}', str(mq)))

# 输入输出占比（基于本周）
ii = wi/max(wi+wo,1)*100
oi = 100 - ii
lines.append(mid_divider(f' 输入{ii:.0f}%  输出{oi:.0f}% '))

# 群组明细（近30天，按消耗量倒序）
try:
    all_registered = [g["name"] for g in
        json.load(open("/workspace/ipc/available_groups.json"))["groups"]
        if g.get("isRegistered")]
except:
    all_registered = []

month_total = max(mi+mo, 1)
group_rows = []
for container, (ti, to, q) in sorted(data_month.items(), key=lambda x: -(x[1][0]+x[1][1])):
    pct = (ti+to)/month_total*100
    group_rows.append((display_name(container), M(ti+to), f'{pct:.0f}%', str(q)))

for row in group_rows:
    lines.append(data_row(*row))

lines.append(border('└','┘'))

print("```\n" + "\n".join(lines) + "\n```")
