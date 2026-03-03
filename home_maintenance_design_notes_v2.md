# Home Maintenance Tracker v2 — Design Notes

## What Changed From v1

The original schema put recurring schedules, one-off projects, and someday items all in one `task_definitions` table. This led to fields that only applied to some rows, branching CASE logic in views, and semantic weirdness (a one-off "paint the bedroom" isn't a "definition" of anything). v2 splits them into purpose-built tables.

## Schema Overview

Seven tables, five views:

```
locations ──┬── assets ──┬── schedules ──── work_log ── documents
             │            ├── projects  ────┘
             │            └── issues ─────── documents
             ├── schedules
             ├── projects
             └── issues
```

**locations** — Flat list of zones in the house. No hierarchy (YAGNI for a home).

**assets** — Physical things: furnace, water heater, roof. Tracks make/model, install date, warranty, and expected lifespan.

**schedules** — Recurring maintenance ONLY. "Replace air filter every 30 days." Every field on this table is relevant to every row. Clean.

**projects** — One-off work items AND someday/wish list. Has its own `status` field (`someday`, `pending`, `in_progress`, `done`, `cancelled`) so it manages its own lifecycle without piggybacking on something else.

**issues** — Observations about condition. "Garage door wasn't installed well." NOT action items. Can optionally link to a project when you decide to fix it.

**work_log** — Completion records. Links to a schedule (recurring), a project (one-off), or neither (ad-hoc). Has a CHECK constraint preventing a row from linking to both a schedule and a project.

**documents** — File attachments. Can link to an asset, work_log entry, issue, OR project. (So you can attach a contractor estimate to a project before any work is logged.)

## Why This Decomposition

Each table represents one clear concept:

| Concept | Table | Has its own lifecycle? |
|---|---|---|
| "Do X every Y days" | `schedules` | Interval-based, tracked via work_log |
| "Need to do X (sometime)" | `projects` | Status-based (pending → done) |
| "X isn't in great shape" | `issues` | Status-based (open → resolved) |
| "I did X on this date" | `work_log` | Immutable history |
| "I own X" | `assets` | Lifecycle via install_date + lifespan |

No table is trying to be two things. The views don't need branching CASE logic to handle different "types" of rows.

## Key Views

**v_schedule_status** — Dashboard for recurring maintenance. Shows overdue / due_soon / ok / never_done. This is the main notification driver.

**v_active_projects** — Your to-do list. Excludes done/cancelled. Sorts by priority, with someday items last. Shows overdue/due_soon based on target_date if set.

**v_open_issues** — State of the house. All unresolved issues sorted by severity.

**v_spending_log** — All spending from work_log, with work type and asset category. Individual entries — aggregate in app code as needed.

**v_asset_lifecycle** — Asset ages, replacement timelines, warranty status, and open issue counts.

## Notification Strategy (ntfy)

```python
# Recurring maintenance
overdue = query("SELECT * FROM v_schedule_status WHERE status = 'overdue'")
due_soon = query("SELECT * FROM v_schedule_status WHERE status = 'due_soon'")

# Projects with deadlines
proj_overdue = query("SELECT * FROM v_active_projects WHERE effective_status = 'overdue'")
proj_soon = query("SELECT * FROM v_active_projects WHERE effective_status = 'due_soon'")

if overdue or proj_overdue:
    ntfy.send(title="🔴 Overdue", message=format_list(overdue + proj_overdue), priority=4)
if due_soon or proj_soon:
    ntfy.send(title="🟡 Coming up", message=format_list(due_soon + proj_soon), priority=3)

# Someday items and issues are never nagged — review manually
```

## Season Hints

Only on `schedules` (where it belongs). Filter in notification logic:

```python
current_month = now.month
if current_month in (3, 4, 5):
    season = 'spring'
elif current_month in (9, 10, 11):
    season = 'fall'
```

## Impact — Why Does This Task Matter?

`impact` is on both `schedules` and `projects`. It captures what happens if you skip or defer the task, which is orthogonal to priority (how soon). A cosmetic paint job can be high priority before guests arrive; a critical weatherproofing task can be low priority in June.

| Value | Meaning | Example |
|---|---|---|
| `safety` | Fire, CO, electrocution, structural collapse | Smoke detectors, dryer vent, GFCI outlets |
| `protective` | Prevents water/weather/pest damage to the house | Gutters, caulking, winterizing faucets, roof inspection |
| `efficiency` | Saves energy/money, extends equipment life | HVAC filters, weatherstripping, condenser cleaning |
| `cosmetic` | Appearance only | Deep clean carpet, painting |
| `comfort` | Quality of life, cleanliness, convenience | Dishwasher filter, drain flushing, range hood |

The key question impact answers: **"Money and time are tight — what can I safely skip?"** Filter by impact to defer `comfort` and `cosmetic` tasks while keeping `safety` and `protective` on track.

Notification filtering example:
```python
# Winter mode: only nag about safety and protective tasks
WHERE impact IN ('safety', 'protective')

# Full mode: everything except cosmetic
WHERE impact != 'cosmetic'
```

## Logging Completed Work

**Recurring maintenance:**
```sql
INSERT INTO work_log (schedule_id, completed_at, performed_by, cost, notes)
VALUES (?, datetime('now'), 'self', 0, 'Replaced with MERV 11 filter');
```
This automatically updates `v_schedule_status` since it calculates from `MAX(completed_at)`.

**Completing a project:**
```sql
-- Log the work details
INSERT INTO work_log (project_id, completed_at, performed_by, cost, notes)
VALUES (?, datetime('now'), 'Acme Doors Inc', 1200, 'Installed fiberglass door with sidelights');

-- Mark the project done
UPDATE projects SET status = 'done', completed_at = datetime('now'), updated_at = datetime('now')
WHERE id = ?;

-- If it was linked to an issue, resolve that too
UPDATE issues SET status = 'resolved', resolved_at = datetime('now'), updated_at = datetime('now')
WHERE project_id = ?;
```

**Ad-hoc / unplanned work:**
```sql
INSERT INTO work_log (asset_id, completed_at, performed_by, cost, notes)
VALUES (?, datetime('now'), 'self', 45, 'Garbage disposal died, replaced with InSinkErator Badger 5');
```

## Issue → Project Flow

When you decide to act on a known issue:

```sql
-- Create the project
INSERT INTO projects (name, category, priority, asset_id, notes)
VALUES ('Get garage door realigned', 'Exterior', 'normal', ?, 'Tracks misaligned per inspector');

-- Link the issue
UPDATE issues SET status = 'scheduled', project_id = last_insert_rowid(), updated_at = datetime('now')
WHERE id = ?;
```

## Someday List

Someday tasks use `status = 'someday'`:

```sql
INSERT INTO projects (name, category, status, notes)
VALUES ('Paint interior walls', 'Interior', 'someday',
        'Previous owners'' color choices are questionable but livable');
```

When ready to commit:
```sql
UPDATE projects SET status = 'pending', priority = 'normal', target_date = '2026-09-01',
       updated_at = datetime('now')
WHERE id = ?;
```

## Five Types of Work

| What | Where | Notifications? |
|---|---|---|
| Recurring maintenance | `schedules` + `work_log` | Yes — overdue/due_soon |
| Planned one-off projects | `projects` | Yes, if target_date set |
| Someday/wish list | `projects` (status='someday') | Never |
| Known conditions/defects | `issues` | Never — manual review |
| Unplanned repairs | `work_log` (no schedule or project) | N/A — already done |

## Seed Data Notes

The seed file includes ~40 common recurring schedules for a Kansas home. A few are **inactive by default** (septic, chimney) with `active=0`. After initial setup:

1. Add your actual locations
2. Add your assets with make/model/install dates
3. Review seed schedules — deactivate what doesn't apply, adjust frequencies
4. Add your known issues (garage door, walls, etc.)
5. Create projects for anything you plan to act on
6. Backfill any known completion dates into work_log
7. Set up the notification automation

## Future Ideas

- **Photo comparison**: Baseline photos of foundation, roof, caulking. Compare year over year via documents.
- **Cost forecasting**: Based on asset ages and expected lifespans, predict upcoming big expenses.
- **Contractor contacts**: Simple table linking contractors to categories with notes on past experience.
- **Weather integration**: Kansas severe weather alerts could trigger ad-hoc inspection projects.
