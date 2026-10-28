"""
gb-my-team: fetch_data.py

Downloads the published Google Sheet (.xlsx), reads the Config tab, parses the
Yahoo IMPORTHTML tables, matches players by name, computes replacement lines
and the two lenses (FOR ME = team log starts, OVERALL = all games), and writes
data/data.json.

Run in GitHub Actions:      python fetch_data.py
Test against a local file:  python fetch_data.py --file path/to/workbook.xlsx

No Yahoo API, no cookies. Python never contacts Yahoo. See SPEC.md.
"""

import io
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.request
from datetime import datetime, date, timedelta, time as dtime
from zoneinfo import ZoneInfo

import openpyxl

# ----------------------------------------------------------------------------
# FIXED SETTINGS (everything tunable lives in the sheet's Config tab)
# ----------------------------------------------------------------------------

SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTL-UN55CMJ7OxsyjMrsnX1zQWZsBOgq6LpdQpQvKL-buXcVKGbaT-AL-5p-1llxnGmkpUUwth2l1sn"
    "/pub?output=xlsx"
)
OUT_PATH = os.path.join("data", "data.json")
NY = ZoneInfo("America/New_York")

WINDOWS = ["season", "l30", "l14"]
WINDOW_LABEL = {"forme": "For me", "season": "Season", "l30": "L30", "l14": "L14"}
POSITIONS = ["G", "F", "C"]
LINES = ["G", "F", "C", "ALL"]
STATS = ["PTS", "REB", "AST", "ST", "BLK", "TO"]

INJURED_TAGS = {"INJ", "O"}
TAGS = ["SUSP", "INJ", "GTD", "DTD", "NA", "O", "Q", "P"]  # longest first
NOTE_TEXT = ["No new player Notes", "New Player Note", "Player Note"]
STATUS_ALIASES = {
    "active": "Active", "injured": "Injured", "inj": "Injured", "il": "Injured",
    "cut": "Cut", "dropped": "Cut", "inactive": "Cut",
}
NBA_TEAMS = {
    "ATL", "BOS", "BKN", "BRK", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GS", "GSW",
    "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NO", "NOP", "NY", "NYK",
    "OKC", "ORL", "PHI", "PHO", "PHX", "POR", "SA", "SAS", "SAC", "TOR", "UTA", "UTAH",
    "WAS", "WSH",
}

TAB_OVERRIDES = "Status Overrides"
TAB_NAMEFIX = "Name Fixes"
TAB_CONFIG = "Config"

DEFAULTS = {
    "team_name": "Marion HoF 2027",
    "masthead": "Marion Hall of Fame",
    "season_label": "2026-27",
    "tab_my_season": "My Team Season",
    "tab_my_l30": "My Team L30",
    "tab_my_l14": "My Team L14",
    "tab_team_log": "My Team Game Log",
    "tab_fa_season_1": "FA Season 1-25",
    "tab_fa_season_2": "FA Season 26-50",
    "tab_fa_l30_1": "FA L30 1-25",
    "tab_fa_l30_2": "FA L30 26-50",
    "tab_fa_l14_1": "FA L14 1-25",
    "tab_fa_l14_2": "FA L14 26-50",
    "w_PTS": 1, "w_REB": 1.2, "w_AST": 1.5, "w_ST": 3, "w_BLK": 3, "w_TO": -1,
    "pool_size": 5,
    "min_gp_pct": 0.5,
    "flag_window": "L30",
    "replace_threshold": -50,
    "ppg_trend_pct": 0.15,
    "mpg_trend_pct": 0.10,
    "small_sample_starts": 5,
    "stale_days": 2,
    "max_gp": 82,
}
NUMERIC_KEYS = {k for k, v in DEFAULTS.items() if isinstance(v, (int, float))}

WARNINGS = []


def warn(msg):
    if msg not in WARNINGS:
        WARNINGS.append(msg)
    print("WARNING:", msg)


# ----------------------------------------------------------------------------
# SMALL HELPERS
# ----------------------------------------------------------------------------

def clean_text(v):
    if v is None:
        return ""
    return str(v).strip()


def to_num(v):
    """Yahoo cells: numbers, '-' for none, sometimes strings."""
    if v is None:
        return 0.0
    if isinstance(v, bool):
        return float(v)
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "")
    if s in ("", "-", "--", "N/A"):
        return 0.0
    if s.endswith("%"):
        try:
            return float(s[:-1]) / 100.0
        except ValueError:
            return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def to_own(v):
    """% Ros arrives as a fraction (0.87) or a percent (87). Return percent."""
    x = to_num(v)
    return round(x * 100 if x <= 1 else x, 1)


def to_minutes(v):
    """MPG / MIN*: Google reads Yahoo's 'mm:ss' as hours:minutes.
    A '34:00' cell arrives as 1 day 10 hours, so minutes = the value in hours."""
    if v is None:
        return 0.0
    if isinstance(v, timedelta):
        return v.total_seconds() / 3600.0
    if isinstance(v, dtime):
        return v.hour + v.minute / 60.0 + v.second / 3600.0
    if isinstance(v, datetime):
        # 1899-12-31 style serial dates: hours past the epoch day
        base = datetime(1899, 12, 30)
        return (v - base).total_seconds() / 3600.0
    if isinstance(v, (int, float)):
        return float(v) * 24.0  # fraction of a day
    s = str(v).strip()
    m = re.match(r"^(\d+):(\d{1,2})$", s)
    if m:
        return int(m.group(1)) + int(m.group(2)) / 60.0
    return to_num(s)


def fold(s):
    """Accent-folded, lowercase, no periods/apostrophes, single spaces."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace("ı", "i").replace("ø", "o").replace("đ", "d").replace("ł", "l")
    s = s.lower()
    s = re.sub(r"[.'\u2019]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def r1(x):
    return None if x is None else round(x, 1)


def r2(x):
    return None if x is None else round(x, 2)


# ----------------------------------------------------------------------------
# NAME PARSING (SPEC section 5)
# ----------------------------------------------------------------------------

def strip_tail(name):
    """Remove trailing note text and injury tag. Runs twice (tag can sit
    before or after the note text)."""
    tag = ""
    for _ in range(2):
        for note in NOTE_TEXT:
            if name.endswith(note):
                name = name[: -len(note)].rstrip()
        for t in TAGS:
            if name.endswith(t) and len(name) > len(t):
                prev = name[-len(t) - 1]
                if prev.islower() or prev in ".'\u2019":
                    tag = tag or t
                    name = name[: -len(t)].rstrip()
                    break
    return name.strip(), tag


def parse_name(raw):
    """Returns dict(name, team, pos[list], tag) or None."""
    if raw is None:
        return None
    s = str(raw).split("\n")[0]
    s = re.sub(r"[\ue000-\uf8ff]", "", s).strip()
    m = re.search(r"([A-Z]+)\s*-\s*([GFC](?:\s*,\s*[GFC])*)\s*$", s)
    if not m:
        return None
    caps = m.group(1)
    team = ""
    for n in range(min(4, len(caps)), 1, -1):
        if caps[-n:] in NBA_TEAMS:
            team = caps[-n:]
            break
    if not team:
        team = caps[-3:]
    head = s[: m.start(1)] + caps[: len(caps) - len(team)]
    pos = [p.strip() for p in m.group(2).split(",") if p.strip()]
    name, tag = strip_tail(head.strip())
    if not name:
        return None
    return {"name": name, "team": team, "pos": pos, "tag": tag}


# ----------------------------------------------------------------------------
# WORKBOOK ACCESS
# ----------------------------------------------------------------------------

def download(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            if data[:2] != b"PK":
                raise ValueError("Download is not an .xlsx file")
            return data
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"Download attempt {i + 1} failed: {e}")
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"Sheet download failed: {last}")


def norm_tab(s):
    return clean_text(s).lower()[:31]


def find_sheet(wb, wanted):
    """Match ignoring case, outer spaces, and the 31-character xlsx limit."""
    target = norm_tab(wanted)
    for ws in wb.worksheets:
        if norm_tab(ws.title) == target:
            return ws
    return None


def read_config(wb):
    cfg = dict(DEFAULTS)
    ws = find_sheet(wb, TAB_CONFIG)
    if ws is None:
        warn("No Config tab found. Using built-in defaults.")
        return cfg
    for row in ws.iter_rows(values_only=True):
        if not row or row[0] is None:
            continue
        k = clean_text(row[0])
        if k.lower() == "key" or k not in DEFAULTS:
            continue
        v = row[1] if len(row) > 1 else None
        if v is None or clean_text(v) == "":
            continue
        if k in NUMERIC_KEYS:
            cfg[k] = to_num(v)
        else:
            cfg[k] = clean_text(v)
    return cfg


def get_tab(wb, cfg, key, required=True):
    """Config name first; fall back to the default name with a warning."""
    name = cfg[key]
    ws = find_sheet(wb, name)
    if ws is None and name != DEFAULTS[key]:
        ws = find_sheet(wb, DEFAULTS[key])
        if ws is not None:
            warn(f"Config {key} says '{name}', which isn't a tab. "
                 f"Used '{DEFAULTS[key]}'. Update the Config tab.")
    if ws is None and required:
        warn(f"Missing tab: '{name}' ({key}).")
    return ws


def find_table(ws):
    """Locate the header row by text (a 'GP*' cell), never fixed positions.
    Returns (header_row_index, colmap, opp_header) or None."""
    rows = list(ws.iter_rows(values_only=True))
    for ri, row in enumerate(rows):
        cells = [clean_text(c) for c in row]
        if "GP*" not in cells:
            continue
        cmap = {}
        opp = ""
        for ci, c in enumerate(cells):
            if not c:
                continue
            key = None
            if c in ("Players", "Name"):
                key = "name"
            elif c == "GP*":
                key = "gp"
            elif c.startswith("Fan Pts"):
                key = "fp"
            elif c == "% Ros":
                key = "own"
            elif c in ("MPG", "MIN*"):
                key = "mpg"
            elif c == "Roster Status":
                key = "rstatus"
            elif c.startswith("Opp:"):
                key = "opp"
                opp = c
            elif c in STATS:
                key = c
            if key and key not in cmap:
                cmap[key] = ci
        if "name" in cmap and all(s in cmap for s in STATS):
            return rows, ri, cmap, opp
    return None


def read_players(ws, label, name_fixes, is_log=False):
    """Return list of player records from one tab."""
    out = []
    if ws is None:
        return out, ""
    found = find_table(ws)
    if not found:
        warn(f"Tab '{ws.title}' has no readable player table.")
        return out, ""
    rows, hr, cmap, opp = found
    seen_keys = {}
    for row in rows[hr + 1:]:
        if cmap["name"] >= len(row):
            continue
        raw = row[cmap["name"]]
        txt = clean_text(raw)
        if not txt:
            continue
        if txt.lower().startswith("totals"):
            break
        p = parse_name(raw)
        if p is None:
            warn(f"Unreadable name on '{ws.title}': {txt.splitlines()[0][:60]}")
            continue
        fixed = name_fixes.get(fold(p["name"]))
        if fixed:
            p["name"] = fixed
        p["key"] = fold(p["name"])

        def g(k):
            ci = cmap.get(k)
            return row[ci] if ci is not None and ci < len(row) else None

        p["gp"] = to_num(g("gp"))
        p["st"] = {s: to_num(g(s)) for s in STATS}
        p["fp_yahoo"] = to_num(g("fp")) if "fp" in cmap else None
        p["own"] = to_own(g("own")) if "own" in cmap else None
        p["min_total"] = None
        mv = to_minutes(g("mpg")) if "mpg" in cmap else 0.0
        if is_log:
            p["min_total"] = None  # team log MIN* is usually '-'
        p["mpg"] = mv if not is_log else None
        p["rstatus"] = clean_text(g("rstatus")) if "rstatus" in cmap else ""
        if p["key"] in seen_keys and seen_keys[p["key"]] != (p["team"], tuple(p["pos"])):
            warn(f"Two different players share the name key '{p['name']}' on "
                 f"'{ws.title}'. Add a Name Fixes row for one of them.")
        seen_keys[p["key"]] = (p["team"], tuple(p["pos"]))
        p["src"] = label
        out.append(p)
    return out, opp


def read_two_col(wb, title):
    ws = find_sheet(wb, title)
    out = {}
    if ws is None:
        return out
    for row in ws.iter_rows(values_only=True):
        if not row or len(row) < 2 or row[0] is None or row[1] is None:
            continue
        a, b = clean_text(row[0]), clean_text(row[1])
        if not a or not b or a.lower() in ("player", "raw name"):
            continue
        out[fold(a)] = b
    return out


def pull_date_from(opp, today):
    m = re.search(r"(\d{1,2})/(\d{1,2})", opp or "")
    if not m:
        return None
    mo, dy = int(m.group(1)), int(m.group(2))
    try:
        d = date(today.year, mo, dy)
    except ValueError:
        return None
    if d > today + timedelta(days=31):
        d = date(today.year - 1, mo, dy)
    return d


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------

def main():
    local = None
    if "--file" in sys.argv:
        local = sys.argv[sys.argv.index("--file") + 1]
    try:
        data = open(local, "rb").read() if local else download(SHEET_URL)
    except Exception as e:  # noqa: BLE001
        print(f"STOP: {e}. Live site left unchanged.")
        sys.exit(1)

    wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
    cfg = read_config(wb)
    W = {s: float(cfg["w_" + s]) for s in STATS}
    pool_size = int(cfg["pool_size"])
    flag_w = {"season": "season", "l30": "l30", "l14": "l14"}.get(
        clean_text(cfg["flag_window"]).lower(), "l30")

    name_fixes = read_two_col(wb, TAB_NAMEFIX)
    overrides = {k: STATUS_ALIASES.get(v.lower()) for k, v in
                 read_two_col(wb, TAB_OVERRIDES).items()}

    def fp_of(st):
        return sum(st[s] * W[s] for s in STATS)

    now_ny = datetime.now(NY)
    today = now_ny.date()

    # ---- My team tabs -------------------------------------------------------
    mine = {}
    opp_hdr = ""
    for w in WINDOWS:
        recs, opp = read_players(get_tab(wb, cfg, f"tab_my_{w}"), w, name_fixes)
        mine[w] = {r["key"]: r for r in recs}
        if w == "season":
            opp_hdr = opp
        for r in recs:
            calc = fp_of(r["st"])
            if r["fp_yahoo"] is not None and abs(calc - r["fp_yahoo"]) > 0.5:
                warn(f"Scoring mismatch: {r['name']} ({WINDOW_LABEL[w]}) Yahoo "
                     f"{r['fp_yahoo']:.1f} vs weights {calc:.1f}.")
            if w == "season" and r["gp"] > cfg["max_gp"]:
                warn(f"{r['name']} shows {int(r['gp'])} GP on the Season tab. "
                     f"Check the season year in the link.")
            if cfg["team_name"] and r["rstatus"] and r["rstatus"] != cfg["team_name"]:
                warn(f"{r['name']} on '{WINDOW_LABEL[w]}' tab shows roster "
                     f"'{r['rstatus']}', not '{cfg['team_name']}'.")

    if not mine["season"]:
        print("STOP: My Team Season table is empty or missing. Live site left unchanged.")
        sys.exit(1)

    log_recs, _ = read_players(get_tab(wb, cfg, "tab_team_log"), "forme",
                               name_fixes, is_log=True)
    log = {r["key"]: r for r in log_recs}

    pull = pull_date_from(opp_hdr, today)
    if pull is None:
        warn("Couldn't read the pull date (Opp: M/D header) on My Team Season.")
    elif (today - pull).days > cfg["stale_days"]:
        warn(f"Data looks stale: sheet pulled {pull:%b %d}, "
             f"{(today - pull).days} days ago.")

    # ---- Free agents and replacement lines ---------------------------------
    fa = {}
    lines = {}
    for w in WINDOWS:
        allrecs = []
        for page in ("1", "2"):
            recs, _ = read_players(get_tab(wb, cfg, f"tab_fa_{w}_{page}"), w, name_fixes)
            allrecs.extend(recs)
        seen = set()
        recs = []
        for r in allrecs:
            if r["key"] in seen:
                continue
            seen.add(r["key"])
            r["fp"] = r["fp_yahoo"] if r["fp_yahoo"] is not None else fp_of(r["st"])
            r["ppg"] = r["fp"] / r["gp"] if r["gp"] > 0 else None
            if w == "season" and r["gp"] > cfg["max_gp"]:
                warn(f"Free agent {r['name']} shows {int(r['gp'])} GP on the Season "
                     f"tab. Check the season year in the link.")
            recs.append(r)
        max_gp = max([r["gp"] for r in recs], default=0)
        min_gp = max(1, math.ceil(cfg["min_gp_pct"] * max_gp - 1e-9))
        for r in recs:
            r["q"] = r["gp"] >= min_gp
            r["why"] = "" if r["q"] else f"GP {int(r['gp'])} < {min_gp}"
        lines[w] = {}
        for L in LINES:
            elig = [r for r in recs if r["q"] and (L == "ALL" or L in r["pos"])]
            elig.sort(key=lambda r: r["ppg"] or 0, reverse=True)
            pool = elig[:pool_size]
            gp = sum(r["gp"] for r in pool)
            ppg = sum(r["fp"] for r in pool) / gp if gp else None
            lines[w][L] = {
                "ppg": r2(ppg), "n": len(pool), "min_gp": min_gp,
                "max_gp": int(max_gp),
                "members": [r["name"] for r in pool],
            }
            for r in pool:
                r.setdefault("pool", []).append(L)
            if len(pool) < pool_size:
                warn(f"{WINDOW_LABEL[w]} {L} line uses only {len(pool)} "
                     f"free agents (min GP {min_gp}).")
        fa[w] = [{
            "name": r["name"], "team": r["team"], "pos": r["pos"], "tag": r["tag"],
            "wv": r["rstatus"].startswith("W") if r["rstatus"] else False,
            "own": r["own"], "gp": int(r["gp"]), "fp": r1(r["fp"]),
            "ppg": r2(r["ppg"]), "mpg": r1(r["mpg"]) if r["gp"] else None,
            "st": r["st"], "q": r["q"], "why": r["why"], "pool": r.get("pool", []),
        } for r in recs]

    # ---- Players: roster + team log ----------------------------------------
    roster_keys = list(mine["season"].keys())
    for w in ("l30", "l14"):
        for k in mine[w]:
            if k not in roster_keys:
                roster_keys.append(k)
    keys = roster_keys + [k for k in log if k not in roster_keys]

    roster_last = {r["name"].split()[-1].lower(): r["name"]
                   for k in roster_keys for r in [mine["season"].get(k) or
                                                  mine["l30"].get(k) or mine["l14"].get(k)]}

    players = []
    for k in keys:
        base = mine["season"].get(k) or mine["l30"].get(k) or mine["l14"].get(k)
        lg = log.get(k)
        src = base or lg
        p = {"name": src["name"], "team": src["team"], "pos": src["pos"],
             "tag": (base or {}).get("tag", "")}
        if base is None:
            p["status"] = "Cut"
            last = p["name"].split()[-1].lower()
            if last in roster_last:
                warn(f"Possible name mismatch: '{p['name']}' (team log, Cut) vs "
                     f"'{roster_last[last]}' (roster). Add a Name Fixes row if same player.")
        elif p["tag"] in INJURED_TAGS:
            p["status"] = "Injured"
        else:
            p["status"] = "Active"
        if overrides.get(k):
            p["status"] = overrides[k]
        p["nostarts"] = base is not None and lg is None
        p["w"] = {}
        if lg and lg["gp"] > 0:
            p["w"]["forme"] = {"gp": int(lg["gp"]), "fp": r1(fp_of(lg["st"])),
                               "mpg": None, "st": lg["st"]}
        for w in WINDOWS:
            r = mine[w].get(k)
            if r and r["gp"] > 0:
                p["w"][w] = {"gp": int(r["gp"]), "fp": r1(fp_of(r["st"])),
                             "mpg": r1(r["mpg"]), "st": r["st"], "own": r["own"]}
        players.append(p)

    # ---- Comparison rows ----------------------------------------------------
    def lens(p, lens_key, L):
        d = p["w"].get(lens_key)
        line_w = "season" if lens_key == "forme" else lens_key
        line = lines[line_w][L]["ppg"]
        if not d or d["gp"] <= 0:
            return None
        ppg = d["fp"] / d["gp"]
        gap = ppg - line if line is not None else None
        return {"gp": d["gp"], "ppg": r2(ppg), "fp": d["fp"],
                "gap": r2(gap), "pts": r1(gap * d["gp"]) if gap is not None else None}

    def ratio(a, b):
        return r2(a / b - 1) if a is not None and b else None

    def make_row(i, p, L, shown_pos):
        c = {lk: lens(p, lk, L) for lk in ["forme"] + WINDOWS}
        flags = []
        fl = c.get(flag_w)
        if p["status"] != "Cut" and fl:
            if fl["pts"] is not None and fl["pts"] < cfg["replace_threshold"]:
                flags.append("Replace?")
            if fl["gap"] is not None and fl["gap"] < 0:
                flags.append("Poor performer")
        notes = list(flags)
        fm = c["forme"]
        if fm and fm["gp"] < cfg["small_sample_starts"]:
            notes.append("Small sample")
        if p["nostarts"]:
            notes.append("No starts yet")
        s, l30, l14 = (p["w"].get(x) for x in WINDOWS)
        return {
            "p": i, "pos": shown_pos, "line": L, "c": c, "flags": flags,
            "notes": notes, "small": bool(fm and fm["gp"] < cfg["small_sample_starts"]),
            "pt": ratio(l30 and l30["fp"] / l30["gp"], s and s["fp"] / s["gp"]),
            "mt": ratio(l14 and l14["mpg"], s and s["mpg"]),
        }

    rows_pos, rows_all = [], []
    for i, p in enumerate(players):
        for L in p["pos"]:
            if L in POSITIONS:
                rows_pos.append(make_row(i, p, L, L))
        rows_all.append(make_row(i, p, "ALL", ",".join(p["pos"])))

    # ---- Upgrade over: my weakest Active player per window and line ---------
    weakest = {}
    for w in WINDOWS:
        weakest[w] = {}
        for L in LINES:
            cands = [(p["w"][w]["fp"] / p["w"][w]["gp"], p["name"]) for p in players
                     if p["status"] == "Active" and w in p["w"]
                     and (L == "ALL" or L in p["pos"])]
            if cands:
                ppg, nm = min(cands)
                weakest[w][L] = {"name": nm, "ppg": r2(ppg)}

    out = {
        "meta": {
            "masthead": cfg["masthead"], "team": cfg["team_name"],
            "season_label": cfg["season_label"],
            "updated": now_ny.strftime("%a %b %-d, %-I:%M %p ET"),
            "pull_date": pull.strftime("%a %b %-d") if pull else None,
            "weights": W, "flag_window": flag_w,
            "replace_threshold": cfg["replace_threshold"],
            "ppg_trend_pct": cfg["ppg_trend_pct"], "mpg_trend_pct": cfg["mpg_trend_pct"],
            "pool_size": pool_size, "min_gp_pct": cfg["min_gp_pct"],
        },
        "warnings": WARNINGS,
        "lines": lines,
        "players": players,
        "rows": {"pos": rows_pos, "all": rows_all},
        "fa": fa,
        "weakest": weakest,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"Wrote {OUT_PATH}: {len(players)} players, "
          f"{sum(len(v) for v in fa.values())} free agent rows, "
          f"{len(WARNINGS)} warnings.")


if __name__ == "__main__":
    main()
