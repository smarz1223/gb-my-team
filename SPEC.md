# gb-my-team SPEC (v1.0, 2026-10-28)

Personal fantasy basketball analysis for Marz's Game...Blouses team ("Marion HoF 2027").
Masthead: **Marion Hall of Fame**
Template: `smarz1223/td-my-team` SPEC v1.2 (hockey). Differences are called out below.

Built 2026-10-28 against the workbook with Config and renamed tabs.

---

## 0. Purpose

Answer two questions for every player on my team, each compared to available free agents by position:

| Lens | Question | Source |
|---|---|---|
| **FOR ME** | How has he scored in games he STARTED for me? | My Team Game Log tab |
| **OVERALL** | How has he scored in ALL his games, started or not? | My Team Season / L30 / L14 tabs |

No snapshots and no history storage. Every run rebuilds from the sheet as it stands that morning.

---

## 1. Hosting

- Repo: `smarz1223/gb-my-team` (separate from the `game-blouses` league site)
- URL: `smarz1223.github.io/gb-my-team/` (unlisted, no password, not linked from the hub)
- Refresh: GitHub Actions daily cron `30 12 * * *` (7:30 AM EST / 8:30 AM EDT), plus manual run button. Cron runs on UTC, so one fixed time drifts 1 hour with DST. 12:30 UTC keeps the run after late West Coast games all season.
- Timestamps: real `America/New_York` timezone (fixes the TD fixed-offset bug).
- Rule: never patch generated HTML. Change the Python and rebuild.

## 2. Data source (no API, no cookies)

Only source: the published Google Sheet (.xlsx export). The sheet's IMPORTHTML formulas pull public Yahoo pages. Python never contacts Yahoo.

`https://docs.google.com/spreadsheets/d/e/2PACX-1vTL-UN55CMJ7OxsyjMrsnX1zQWZsBOgq6LpdQpQvKL-buXcVKGbaT-AL-5p-1llxnGmkpUUwth2l1sn/pub?output=xlsx`

### Tabs read

Tab names come from the **Config** tab (section 3). If a Config name isn't found, the code falls back to the default name and shows a data-check warning. Matching ignores leading and trailing spaces and case.

**Excel limit:** the .xlsx export cuts tab names to 31 characters ("All Available Season Total 26-50" arrives as "...26-5"). Matching uses the first 31 characters of the Config value.

| Config key | Tab name (default) | Holds | All columns are |
|---|---|---|---|
| `tab_my_season` | My Team Season | Current roster, all games | Totals |
| `tab_my_l30` | My Team L30 | Same, last 30 days | Totals |
| `tab_my_l14` | My Team L14 | Same, last 14 days | Totals |
| `tab_team_log` | My Team Game Log | Started games only, every player who ever started | Totals, no Fan Pts |
| `tab_fa_season_1` / `_2` | FA Season 1-25 / FA Season 26-50 | Free agents 1-25 / 26-50 | Totals |
| `tab_fa_l30_1` / `_2` | FA L30 1-25 / FA L30 26-50 | Same | Totals |
| `tab_fa_l14_1` / `_2` | FA L14 1-25 / FA L14 26-50 | Same | Totals |
| n/a | Status Overrides (optional) | Columns: Player, Status (Active, Injured, Cut) | n/a |
| n/a | Name Fixes (optional) | Columns: Raw Name, Use Name | n/a |

### Reading rules

- Find each table by header text (`Players` row with `GP*` and `Fan Pts`, or `Name` with `GP*` on the team log), never fixed rows or columns.
- Read raw Yahoo columns only: name string, Roster Status, GP*, Fan Pts, % Ros, MPG, PTS, REB, AST, ST, BLK, TO.
- GP shown as `-` = 0.
- **MPG conversion:** Google reads Yahoo's "34:00" as hours. Minutes = the cell's value in hours (a 1-day-10-hour value = 34.0 min).
- PPG = Fan Pts / GP on every tab (all tabs are totals, unlike TD's Avg tabs).
- Pull date comes from the `Opp: M/D` header (staleness check).
- A missing optional tab is fine. A missing required tab shows in the data-check bar; the rest of the site still builds.

## 3. Config tab

Two columns: **Key**, **Value**. Any missing key uses the default shown.

| Key | Default | Notes |
|---|---|---|
| `team_name` | Marion HoF 2027 | Must match Roster Status on my-team tabs |
| `masthead` | Marion Hall of Fame | |
| `season_label` | 2026-27 | |
| `tab_*` (10 keys) | Default names in section 2 | |
| `w_PTS` / `w_REB` / `w_AST` / `w_ST` / `w_BLK` / `w_TO` | 1 / 1.2 / 1.5 / 3 / 3 / -1 | Scoring weights |
| `pool_size` | 5 | Top N free agents per line |
| `min_gp_pct` | 0.5 | See section 7 |
| `flag_window` | L30 | Window that drives Replace? and Poor performer |
| `replace_threshold` | -50 | Pts over replacement |
| `ppg_trend_pct` | 0.15 | Arrow when L30 vs Season PPG moves beyond this |
| `mpg_trend_pct` | 0.10 | Arrow when L14 vs Season MPG moves beyond this |
| `small_sample_starts` | 5 | |
| `stale_days` | 2 | |
| `max_gp` | 82 | Season GP above this = stale season link warning |

## 4. Scoring

| Stat | PTS | REB | AST | ST | BLK | TO |
|---|---|---|---|---|---|---|
| Pts | 1 | 1.2 | 1.5 | 3 | 3 | -1 |

- Verified 2026-10-27: Sengun 194.2, Jabari Smith Jr. 137.4 (calculated = Yahoo).
- Team log has no Fan Pts column. Points are calculated from stats.
- Roster: G, G, F, F, C, Util, BN, IL x5.

## 5. Name parsing and matching

Example raw string: `Alperen ŞengünONew Player NoteHOU - F,C`

1. Keep the first line only (drops game time).
2. Remove icon characters (Unicode private-use range).
3. Read `TEAM - POS` from the end. POS is a comma list of G, F, C. TEAM uses a known NBA abbreviation list, longest first (Yahoo uses GSW, not GS).
4. Strip note text from the end of the name: `Player Note`, `New Player Note`, `No new player Notes`.
5. Strip injury tag from the end of the name: `INJ`, `GTD`, `DTD`, `O`, `Q`, `P`, `SUSP`, `NA` (Yahoo NBA uses O = out, Q = questionable, P = probable). Counts as a tag only when the character before it is lowercase, a period, or an apostrophe. Loop runs twice (tag before note). Save as tag.
6. Apply Name Fixes tab if present.

Match key = accent-folded lowercase name, periods and apostrophes removed. **No position group in the key** (basketball has one player table, and multi-position eligibility changes during the season). Team is not in the key (trades do not break matches).

Duplicate guard: if two different players on one tab produce the same key, the data-check bar flags it. Fix with the Name Fixes tab (e.g. add a team suffix to one).

Verified 2026-10-27: every name on every tab parsed, including Ingram (`LAC - G,F`, tag O).

## 6. Player status (no history needed)

| Status | Rule | Example (10/27) |
|---|---|---|
| Active | On roster pull, tag none, GTD, DTD, Q, or P (badge shown) | Cunningham |
| Active, no starts yet | On roster pull, not in team log. FOR ME blank | none today |
| Injured | On roster pull, tag INJ or O | Ingram (O), Sengun (O) |
| Cut | In team log, not on roster pull. FOR ME only | Okongwu |
| Override | Status Overrides tab wins over all rules | n/a |

**Decided:** `INJ` and `O` = Injured. Yahoo's `O` can mean out for one night, and the sheet does not show roster slots, so a healthy player can show Injured for a day (Sengun on 10/27). Use Status Overrides for a lasting exception. Injured players stay in the default view (Status slicer default: Active + Injured).

## 7. Replacement baselines

Positions: **G, F, C**, plus **ALL** (all free agents combined, duplicates removed). No separate Util line (ALL covers it).
Windows: Season, L30, L14. Each window has its own free agent pull (50 players) and its own lines.

| Rule | Value |
|---|---|
| Ownership floor | None |
| Min GP | 50% of the highest GP by any free agent in that window's pull, rounded up |
| Pool | Top 5 by PPG among qualifiers, per position |
| Line PPG | GP-weighted: sum of Fan Pts / sum of GP across the pool |
| Short pool | Use those that qualify and show the count, e.g. (3) |

- Example: L30 max free agent GP = 12, so min GP = 6.
- Rounding is up (max 11 → min 6). Max is taken across all 50 free agents in the window, not per position.
- The 50% rule scales with the season, so TD's early-season fallback is dropped.
- A multi-position free agent counts in every pool he is eligible for (F,C goes in F and C).

## 8. Comparisons

- **Position mode:** a multi-position player gets one row per eligible position (Sengun shows under F and C). Each row is measured against that position's line.
- **All players mode:** one row per player, measured against the ALL line.
- PPG gap = his PPG minus line PPG. Pts over replacement = PPG gap x GP.

| Lens | Windows | Line used |
|---|---|---|
| FOR ME | Team log (whole stint) | Season |
| OVERALL | Season, L30, L14 | Matching window |

## 9. Notes column (flags)

Flags are row-level, so a player can be flagged at F but not at C.

| Note | Rule | Slicer? |
|---|---|---|
| Replace? | OVERALL L30 pts over replacement below -50 | Yes |
| Poor performer | OVERALL L30 PPG below the row's line | Yes |
| Small sample | Fewer than 5 starts for me (FOR ME cells grayed) | No |
| No starts yet | On roster, not in team log | No |

Trend columns:
- **PPG trend:** L30 PPG / Season PPG - 1, arrow beyond +/-15%.
- **MPG trend (new):** L14 MPG / Season MPG - 1, arrow beyond +/-10%. Role-change signal.

## 10. Pages and controls

Page buttons (My Team, Waiver Wire) in the title bar. Slicers in one panel below. Tables redraw in place.

**Total FP** column (PPG x GP) next to PPG on every table.

**My Team**
- View: vs Replacement (GP, PPG, +/- PPG, +/- Pts for For me, Season, L30, L14) or Stat line (one window at a time).
- Compare to: Position or All players.
- Stat line only: Window (For me, Season, L30, L14) and Stats as (raw stats or fantasy points by category).
- Slicers (multi-select): Position (G, F, C; union), Status (Active, Injured, Cut; Cut off by default), Flags (Poor performer, Replace?; must match all picked). Clear slicers resets these three only.
- Replacement line table above, collapsible.
- Default sort: Pos (G, F, C order), then PPG.

**Waiver Wire**
- Position (G, F, C, All), Window (Season, L30, L14), Show (Per game / Totals), Stats as (raw / fantasy pts), Show my team (on by default), Show disqualified (off by default; reason shown next to name, e.g. "GP 4 < 6").
- Defaults: All, L30, Per game, sorted by PPG descending.
- My team rows: Active and Injured players eligible at the selected position with GP in that window, blue rows with a "Mine" tag. Cut players and 0 GP excluded.
- Columns: pool star, player, pos, team, own %, GP, MPG, PPG, +/- line, per-game stats (PTS, REB, AST, ST, BLK, TO), Upgrade over.
- Upgrade over = my weakest Active player eligible at the position, same window, PPG gain (positive only).

**All tables**
- Click any column header to sort; click again to reverse.
- +/- columns: diverging color, red to white (0) to green, scaled to the largest absolute value shown.
- Stat, PPG, and MPG columns: 3-color scale (min red, median white, max green). More fantasy points = greener. TO reversed in raw mode (fewer = greener).
- Sticky header row and player column. Horizontal scroll on narrow screens.

**Data-check bar:** red bar at the top, only when a warning exists (stale pull, missing or empty tab, unreadable name, possible name mismatch, scoring mismatch over 0.5, Season GP over `max_gp`).

## 11. Look and feel

- Function over form. Light Excel-style grid, same layout as TD. Always light (no dark mode), page #fbf8f2, tables white.
- Basketball court accent only: light maple title bar (#efd9b4) with orange baseline, court stripe (blue paint, white center circle and arcs), small ball icon, dark wood text (#4a2c0c). Active chips in court blue (#3d6fb6).
- Notes column sits right after Pos on My Team so flags are visible without scrolling.
- Body and tables: Segoe UI / Calibri system font.
- Scale colors: green 99,190,123 / red 248,105,107 (same as all sites).

## 12. Repo files

| File | Purpose |
|---|---|
| `fetch_data.py` | Download sheet, read Config, parse, match, compute, write `data/data.json` |
| `build.py` | Generate `index.html` from `data/data.json` |
| `.github/workflows/refresh.yml` | Daily cron + manual run, commits data and HTML |
| `data/data.json` | Generated each run (do not edit) |
| `index.html` | Generated each run (do not edit) |
| `SPEC.md` | This file |

## 13. Out of scope (decided)

No snapshots, no This Week or games-remaining view, no "since dropped" tracking, no Day by Day, no Player Detail page, no headlines, no ownership floor, no L7, no Yahoo API or cookies.

## 14. Safety rules in the code

- If the sheet download fails or the roster tables are empty, the run stops and the live site is left unchanged.
- Fan Pts on my-team rows are checked against the scoring weights; mismatches over 0.5 are reported.
- A Cut player sharing a last name with a roster player is flagged as a possible name mismatch.
- Two different players with the same match key on one tab are flagged (see section 5).

## 15. Season rollover checklist

- Update the Season `stat1` year in the IMPORTHTML links on: My Team Season tab and both FA Season tabs.
- Update `season_label` in Config.
- Confirm `team_name` in Config and the team log URL if the league ID or team number changes.
- Re-check scoring weights and roster positions in Yahoo settings.

## 16. Known issues

- Cron runs on UTC, so the refresh lands at 8:30 AM ET during daylight time (Mar to Nov).
- Yahoo's `O` tag can mark a healthy player Injured for a day (use Status Overrides if it sticks).
- A name ending in a capital letter (e.g. "III") won't have a trailing tag stripped. Add a Name Fixes row if one shows up unreadable.
