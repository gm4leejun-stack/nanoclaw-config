import json, os, sqlite3
from datetime import datetime, timezone, timedelta

tz_beijing = timezone(timedelta(hours=8))
now = datetime.now(tz_beijing)
today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
week_start  = today_start - timedelta(days=today_start.weekday())
month_start = today_start - timedelta(days=29)

# ── 1. 读取容器显示名映射 ──────────────────────────────────────────
# 配置文件在 nanoclaw-config/data/container_aliases.json
# restore.sh 会将其复制到 /workspace/group/data/
ALIASES_FILE = os.path.join(os.path.dirname(__file__), "container_aliases.json")
try:
    display_map = {k: v for k, v in json.load(open(ALIASES_FILE)).items()
                   if not k.startswith("_")}
except:
    display_map = {}

def display_name(container):
    if container in display_map:
        return display_map[container]
    # fallback：去掉 telegram_ 前缀
    return container.replace("telegram_", "").replace("_", "-")

# ── 2. 同步 JSONL → SQLite ─────────────────────────────────────────
usage_dir = "/workspace/shared/usage"
db_path   = os.path.join(usage_dir, "usage.db")

def sync_to_sqlite():
    con = sqlite3.connect(db_path)
    con.execute("""CREATE TABLE IF NOT EXISTS usage (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        ts        TEXT NOT NULL,
        container TEXT NOT NULL,
        input     INTEGER NOT NULL,
        output    INTEGER NOT NULL
    )""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_ts ON usage(ts)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_container ON usage(container)")

    # 读取每个容器已同步的最新时间戳
    synced = {r[0]: r[1] for r in con.execute(
        "SELECT container, MAX(ts) FROM usage GROUP BY container")}

    new_rows = []
    for fname in os.listdir(usage_dir):
        if not fname.endswith(".json") or fname == "usage.db": continue
        container = fname[:-5]
        last_ts   = synced.get(container, "")
        with open(os.path.join(usage_dir, fname)) as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    d = json.loads(line)
                    ts = d.get("ts", "")
                    if ts > last_ts:
                        new_rows.append((ts, container, d.get("in", 0), d.get("out", 0)))
                except:
                    pass

    if new_rows:
        con.executemany(
            "INSERT INTO usage (ts, container, input, output) VALUES (?,?,?,?)",
            new_rows)
        con.commit()
    con.close()

sync_to_sqlite()

# ── 3. 查询统计 ────────────────────────────────────────────────────
def query_period(since_ts):
    con = sqlite3.connect(db_path)
    rows = con.execute("""
        SELECT container,
               SUM(input)  AS i,
               SUM(output) AS o,
               COUNT(*)    AS q
        FROM usage
        WHERE ts >= ?
        GROUP BY container
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

# ── 4. 格式化输出 ──────────────────────────────────────────────────
def M(n): return f"{n/1e6:.3f}M"
def usd(i,o): return i*3/1e6 + o*15/1e6
def cny(i,o): return usd(i,o) * 7.2

def color_split_bar(i, o, w=6):
    t = max(i+o, 1)
    fi = round(i/t*w)
    return '🟦'*fi + '🟧'*(w-fi)

L = []
L.append(f"📊 *Token 消耗报告*  _{now.strftime('%m/%d  %H:%M')}_")

def period_row(icon, label, i, o, q):
    ip = i/max(i+o,1)*100; op = 100-ip
    ic = i*3/1e6; oc = o*15/1e6; tc = max(ic+oc,1e-9)
    icp = ic/tc*100
    L.append(f"{icon} *{label}*   {M(i+o)}  ${usd(i,o):.2f}  ¥{cny(i,o):.1f}  {q}次")
    L.append(f"量 ↑{ip:.0f}% {color_split_bar(i,o)} ↓{op:.0f}%")
    L.append(f"价 ↑{icp:.0f}% {color_split_bar(int(ic*1e6),int(oc*1e6))} ↓{100-icp:.0f}%")
    L.append("")

period_row("⏱", "今日", gi, go, gq)
period_row("📅", "本周", wi, wo, wq)
period_row("🗓", "近30天", mi, mo, mq)

# ── 5. 各群组对比（近30天）────────────────────────────────────────
GROUP_COLORS = ['🟦','🟧','🟩','🟥','🟨','🟪']
month_total = max(mi+mo, 1)

# 所有已知容器（有数据的 + 已注册未使用的）
try:
    all_registered = [g["name"] for g in
        json.load(open("/workspace/ipc/available_groups.json"))["groups"]
        if g.get("isRegistered")]
except:
    all_registered = []

containers_with_data = list(data_month.keys())
all_display = [display_name(c) for c in containers_with_data]
extra = [g for g in all_registered if g not in all_display]

group_data = []
for idx, container in enumerate(containers_with_data):
    ti, to, q = data_month[container]
    pct = (ti+to)/month_total*100
    group_data.append((display_name(container), GROUP_COLORS[idx%len(GROUP_COLORS)], ti, to, q, pct))
for gname in extra:
    group_data.append((gname, '⬛', 0, 0, 0, 0.0))

BAR_W = 10
active = [d for d in group_data if d[5] > 0]
stacked = []
if active:
    slots = {i: max(1, round(d[5]/100*BAR_W)) for i,d in enumerate(active)}
    diff = sum(slots.values()) - BAR_W
    if diff != 0:
        biggest = max(range(len(active)), key=lambda i: active[i][5])
        slots[biggest] = max(1, slots[biggest]-diff)
    for i,d in enumerate(active):
        stacked.extend([d[1]]*slots[i])
    while len(stacked) < BAR_W:
        stacked.append('⬜')

L.append("━━━ 各群组（近30天）━━━━━━")
L.append("".join(stacked))
L.append("")
for gname, color, ti, to, q, pct in group_data:
    if q > 0:
        L.append(f"{color} *{gname}*  {M(ti+to)}  {pct:.1f}%  ${usd(ti,to):.2f}  {q}次")
    else:
        L.append(f"⬛ {gname}  —")

print("\n".join(L))
