# Domuscura

## What This Is

A self-hosted home maintenance tracker. It tracks recurring maintenance schedules, one-off projects, known issues, assets, and spending — then notifies you via ntfy when things are overdue or coming due.

The name is Latin: domus (house) + cura (care).

## Why It Exists

There's no mature self-hosted tool for general home maintenance tracking. The closest options are either vehicle-specific (LubeLogger), too immature to rely on (HomeLogger — 5 GitHub stars), general-purpose but not purpose-built (Grocy), or cloud-dependent commercial apps. As a first-time homeowner in Kansas, I need something that understands recurring maintenance, tracks what I've done and spent, nags me about the important stuff, and stays out of the way for the rest.

## Who It's For

Primarily me and my partner Tierra, but designed with eventual open-source in mind. The UI and data model should make sense to anyone maintaining a house, not just the person who built it.

## The Five Types of Work

This is the core mental model. Everything in the app maps to one of these:

1. **Recurring maintenance** — "Replace HVAC filter every 30 days." Interval-based. The system tracks when you last did it and nags you when it's overdue. This is the bread and butter.

2. **Planned projects** — "Replace the front door." One-off work with a status lifecycle (pending → in_progress → done). May or may not have a deadline.

3. **Someday / wish list** — "Paint the interior walls." Projects with status `someday`. No deadlines, no nagging. Just a list of things you'd like to do eventually.

4. **Known issues / observations** — "Garage door tracks are misaligned." These describe the *state* of things, not action items. They sit in a list sorted by severity. When you decide to act, you create a project and link the issue to it.

5. **Unplanned repairs** — "Garbage disposal died, replaced it." There was no schedule or project — something just broke and you fixed it. Logged after the fact directly into the work log.

## Key Concepts

**Priority vs. Impact** — Priority is "how soon" (low/normal/high/critical). Impact is "what happens if I skip it" (safety/protective/efficiency/cosmetic/comfort). These are orthogonal. A cosmetic paint job can be high priority before guests arrive. A critical weatherproofing task can be low priority in June. Impact answers the question: "Money's tight this month — what can I safely defer?"

**Schedules are not projects** — Recurring schedules and one-off projects are separate tables with different fields. A schedule has `frequency_days` and no status. A project has `status` and no frequency. Nothing is trying to be two things.

**Issues are not action items** — An issue is an observation ("the caulking in the master bath is cracking"). It becomes actionable only when you choose to create a project from it. Until then, it's just a record of the house's condition, sorted by severity.

**Work log is immutable history** — Every time you complete a recurring task, finish a project, or do an unplanned repair, a row goes into the work log. This is where cost tracking and interval calculations come from. A work log entry links to a schedule OR a project OR neither (ad-hoc), never both.

**Documents attach to anything** — Receipts, warranties, photos, estimates, manuals. Can be linked to an asset, a work log entry, an issue, or a project. A warranty PDF might live on the asset long-term and also on the work log entry where it was referenced for a claim.

**Season hints** — Some tasks only make sense at certain times of year. "Winterize outdoor faucets" has `season_hint = 'fall'`. The notification logic should respect this so you don't get nagged about winterizing in April.

## Notification Philosophy

The app should nag about:
- Overdue recurring maintenance
- Overdue projects (past target_date)
- Due-soon recurring maintenance (within 85% of interval)
- Due-soon projects (within 14 days of target_date)

The app should NEVER nag about:
- Someday items
- Known issues
- Anything with impact `cosmetic` (unless the user opts in)

Notifications go through ntfy. The notification job should be a scheduled task that queries the views and sends alerts.

## What the UI Needs to Do

**Dashboard** — At a glance: what's overdue, what's coming up, what's the state of the house. This is the screen you look at on a Saturday morning to decide what to do today.

**Log work** — The most common interaction. "I just replaced the HVAC filter." Should be fast — pick the schedule, confirm completion, optionally add notes/cost. One or two taps ideally.

**Manage schedules** — View all recurring schedules, see their status, adjust frequency, activate/deactivate. Seed data provides ~40 common Kansas home tasks as a starting point.

**Manage projects** — Your to-do list for the house. Create, update status, set deadlines, mark done. Includes someday items.

**Manage issues** — Track known conditions. Link to projects when you decide to act. Resolve when fixed.

**Assets** — Your physical inventory. Furnace, water heater, roof, appliances. Install dates, warranties, expected lifespans. The app should surface upcoming replacements.

**Spending** — How much have you spent, on what, when. Aggregation by year, category, work type.

## What's Included

Three files accompany this document:

- **home_maintenance_schema_v2.sql** — Complete SQLite schema (7 tables, 5 views, indexes). This has been through multiple review rounds and is solid. The views do most of the heavy lifting for the dashboard.

- **home_maintenance_seed_data_v2.sql** — ~40 recurring maintenance schedules for a typical Kansas home with inline notes and tips. Meant to be a useful starting point, not just placeholder data.

- **home_maintenance_design_notes_v2.md** — Detailed technical notes on the schema design: why tables are structured the way they are, SQL examples for every workflow, the notification strategy, and future ideas.

The schema is the source of truth. It's been through three rounds of critical review and the decomposition is clean. Build on it directly.

## Kansas-Specific Considerations

This matters because it influences which seed data tasks exist and which are marked critical:

- **Hard water** — Water softener salt is a recurring task. Sediment buildup means flushing the water heater and checking the anode rod are more urgent here than average.
- **Real winters** — Winterizing outdoor faucets is marked critical. A burst pipe from a frozen hose bib can cost thousands.
- **Severe weather** — Hail damage inspections after storms, gutter maintenance to prevent foundation water problems, sump pump testing.
- **Cottonwood season** — AC condenser coils get destroyed by cottonwood fluff every spring.
- **Expansive clay soils** — Foundation and grading inspection is extra important.

## Future Ideas (Not for v1)

- Photo comparison: baseline photos of foundation/roof, compare year over year
- Cost forecasting: predict upcoming expenses based on asset ages and lifespans
- Contractor contacts: track service providers by category
- Weather integration: severe weather alerts trigger inspection projects
