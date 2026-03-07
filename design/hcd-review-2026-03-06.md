# Human-Centered Design Review — 2026-03-06

Live browser review via Playwright. Screenshots in `screenshots/current/`.

---

## Who Is This Person?

A homeowner — not a developer. They open this app while standing in a laundry room holding a dryer duct brush, or sitting at the kitchen table after noticing a leak. They are task-oriented, occasionally distracted, and on their phone as often as at a desktop. They did not design the data model. They do not know what "frequency (days)" means.

Their goal: log that they did something, or find out what's overdue. Fast.

---

## HIGH

### Irreversible "Done" with no confirmation

**Files:** `maintenance/templates/dashboard.html:43-48`, `maintenance/templates/partials/schedule_row.html:20-25`
**Harm:** The "Done" button on the dashboard and schedule list immediately creates an immutable work log entry. Work logs cannot be deleted or edited. A one-tap accident — common when using a phone in gloves, or next to the appliance — permanently corrupts maintenance history. The duplicate log can only be observed, not removed.
**Fix:** Add `hx-confirm="Mark this done?"` to the quick-log submit button, or introduce a lightweight undo window (e.g. 5-second toast with "Undo"). The confirm route is simpler; the undo route is friendlier.
**Status:** Done — `hx-confirm="Mark this done?"` added to all Done forms on dashboard and schedule row partial

---

### Log Work modal: Save button hidden below viewport

**File:** `maintenance/templates/partials/work_log_modal.html`
**Harm:** On a standard laptop viewport the Save button is clipped by the modal bottom edge. On mobile with the keyboard open it is completely invisible — the user has no way to submit without knowing to scroll inside the modal. Per Nielsen: system status must be visible. The submit button is the most important element in the modal.
**Fix:** Make the modal `<article>` use `display: flex; flex-direction: column;` with a scrollable body and a fixed footer containing the submit button. The action buttons should always be visible regardless of form height.
**Status:** Done — modal article is flex-column with overflow-y: auto on the form container; submit button is sticky at the bottom

---

### "Frequency (days)" requires mental arithmetic

**File:** `maintenance/templates/schedules/schedule_form.html` (edit form)
**Harm:** The required field asks for a raw integer: `365` for annually, `90` for quarterly, `730` for every 2 years. A homeowner setting up a new schedule must convert human concepts to machine counts. This is the primary required field — it gates all schedule creation.
**Fix:** Replace the raw `<input type="number">` with a compound picker:
- A number field + unit selector: `[1] [year ▾]` → renders as "Annually"
- Or: keep the raw field but add a live preview label below it: "= every 12 months"
The Frequency Label field already exists for display — tie it to a smart default based on the numeric input.
**Status:** Done — added Alpine.js preset select above the raw fields; selecting a preset auto-fills both frequency_days and frequency_label; raw fields remain editable for custom values

---

## MEDIUM

### Duration not pre-filled from schedule estimate

**File:** `maintenance/templates/partials/work_log_form.html`
**Harm:** The schedule detail shows "Est. Time: 30 min" prominently. The Log Work modal's Duration field is blank. The most useful default (the schedule's own estimate) sits unused. The user must recall and re-enter a number they just read. This is pure friction on the most common action in the app.
**Fix:** Pass `schedule.estimated_time_minutes` to the work log form view and pre-populate `initial={'duration_minutes': schedule.estimated_time_minutes}`.
**Status:** Done — `log_work_form()` sets `initial["duration_minutes"] = schedule.estimated_minutes` when schedule has an estimate

---

### "Discovered Date" in New Issue defaults to empty, not today

**File:** `maintenance/templates/issues/issue_form.html` (new issue form)
**Harm:** Issues are almost always logged the day they're discovered. An empty date field in the common case creates unnecessary work. It also means users who skip the field will have undated issues.
**Fix:** Default `discovered_date` to `date.today()` in the form's `__init__` or the view context. The user can clear it if the issue was found earlier.
**Status:** Done — `IssueForm.__init__` sets `discovered_at` initial to `date.today()` for new instances

---

### "----------" as empty choice label in dropdowns

**Files:** Schedule edit form, Issue new form — Asset, Location, Source, Linked Project dropdowns
**Harm:** Django's default `empty_label="---------"` is developer language. To a homeowner it reads as a broken UI element. It also provides no signal about whether the field is required or what "none" means in context.
**Fix:** Override `empty_label` with natural language per field:
- Asset → "No specific asset"
- Location → "Unspecified"
- Source → "Not recorded"
- Linked Project → "No linked project"
**Status:** Done — `empty_label` overrides added in all four form `__init__` methods (IssueForm, ScheduleForm, ProjectForm, WorkLogForm)

---

### Notes text rendered in orange (warning color) on schedule detail

**File:** `maintenance/templates/schedules/detail.html`, `maintenance/static/css/app.css`
**Harm:** The detail page renders the Notes field in `--color-warning` orange. This is user-entered free text — not a UI warning. The color is borrowed from the "Due Soon" status badge, misappropriating a semantic color token for unrelated content. Visually it implies urgency the designer didn't intend. For users with protanopia the orange reads as gray, losing any intended emphasis without gaining correct semantics.
**Fix:** Remove the warning color from the Notes `<dd>`. Notes are prose — use the default text color. If the intent was to highlight safety-critical notes, introduce a dedicated `is_warning` flag on the schedule model and style that explicitly.
**Status:** Done — Notes `<dd>` has no color override; uses default text color

---

### Spending page: broken 3+1 card grid

**File:** `maintenance/templates/spending/dashboard.html` (or equivalent)
**Harm:** Three summary cards (Last 30 Days, Last 90 Days, Year to Date) sit in a row, and "All Time" is alone on a second row spanning roughly one-third of the width. It looks like a layout bug — a fourth card was removed and the grid wasn't adjusted.
**Fix:** Either arrange as 2×2 (Last 30 / Last 90 / Year to Date / All Time), or make "All Time" span full width as a footer stat below the other three.
**Status:** Done — `.spending-summary` CSS grid uses `grid-template-columns: 1fr 1fr`, giving a 2×2 layout

---

### Spending page: no path forward from empty state

**File:** `maintenance/templates/spending/dashboard.html`
**Harm:** A new user sees 12 rows of "$0, 0 entries". There is no explanation that spending data comes from work logs with a cost, no call to action, and no indication that the page will ever show anything useful. The page appears broken.
**Fix:** Add a conditional empty state: if `total_all_time == 0`, show a brief explanation — "Spending is tracked automatically when you log work with a cost. Try logging work on any schedule."
**Status:** Done — spending view passes `has_any_costs`; template shows explanation banner when no cost data exists

---

## LOW

### "Annually interval" is grammatically wrong

**File:** `maintenance/templates/schedules/detail.html`
**Harm:** The schedule subtitle reads "Annually interval · Critical priority". "Annually interval" is not English. A user who reads it will feel the software is unpolished.
**Fix:** Change to "Annual interval" or just show the frequency label directly: "Annually · Critical priority".
**Status:** Done — frequency labels stand alone; raw day counts render as "every N day(s)"

---

### "Category" and "Impact" both show "Safety" — distinction unclear

**File:** `maintenance/templates/schedules/detail.html`
**Harm:** The detail page shows Category: Safety and Impact: Safety as separate rows. For this schedule they're identical, which raises the question: are these the same field? Why are both shown? A user setting up their own schedule won't know which to fill.
**Fix:** On the detail page, only show Impact if it differs from Category, or collapse them into a single row. On the edit form, add brief helper text distinguishing the two concepts.
**Status:** Done — detail page suppresses Impact row when it matches Category; Impact field on edit form has helper text explaining the distinction

---

### "Season Hint" field has no explanation of effect

**File:** Schedule edit form
**Harm:** The field shows `e.g. "Spring", "Fall"` but nothing explains what this does. Does it show on the dashboard? Affect scheduling? Is it cosmetic? A homeowner filling out the form will skip it or guess.
**Fix:** Add helper text: "Optional — displayed as a reminder of when to do this task (e.g. 'Best done in Fall before heating season')."
**Status:** Done — helper text added to Season Hint field on edit form

---

### "Professional recommended" checkbox has no context

**File:** Schedule edit form
**Harm:** The checkbox exists with no explanation of what it changes in the system. Does it affect display? Generate different reminders? Flag for contractor scheduling? Users can't make an informed choice.
**Fix:** Add helper text: "Mark if this task should be done by a licensed contractor or specialist." If it has no functional effect yet, remove it until it does.
**Status:** Done — helper text added to checkbox on edit form

---

### datetime-local picker for work log completion time

**File:** `maintenance/templates/partials/work_log_form.html`
**Harm:** "Completed at" shows `mm/dd/yyyy, --:-- --` — a datetime-local input requiring both date and time. For home maintenance, the time of day is irrelevant (did you clean the gutters at 2:15pm or 3:00pm?). The extra complexity makes the field more intimidating, and on mobile the time picker is a second interaction step.
**Fix:** Change to `<input type="date">` and store only the date. If exact timestamps are needed for audit purposes, store server-side `created_at` automatically — don't burden the user with it.
**Status:** Done — WorkLogForm uses DateInput; clean_completed_at converts date → midnight datetime

---

### Schedule detail: Status card has large empty whitespace

**File:** `maintenance/templates/schedules/detail.html`
**Harm:** The two-column layout places Details (left, dense) next to Status (right, sparse: "Status / Mark Done / Never completed — no work logs yet"). The right card has a large empty white box beneath the content. It looks like something is missing.
**Fix:** For the empty-history state, the Status card could include the Log Work form inline (already available via HTMX). Or the two-column layout could collapse to single-column until there's history to display.
**Status:** Done — "Log Work with Details" button shown in status card when never_done; work_log_modal included on detail page

---

## Additional Issues (UX / Data / Information Architecture)

### "Mark Done" records nothing — no cost, duration, or notes

**Files:** `maintenance/templates/dashboard.html`, `maintenance/templates/partials/schedule_row.html`
**Harm:** The primary quick-action button creates a bare work log with only a timestamp. Users who want to record what they spent, how long it took, or any notes must know to use the separate "Log Work" path instead. Most won't — so the majority of work logs will be empty, making the Spending dashboard permanently useless.
**Fix:** Replace the bare "Done" quick-log with the full Log Work modal, pre-populated to make submission fast (date = today, duration = estimated time). The modal can be dismissed in one tap if users only want to mark done with no details.
**Status:** Open

---

### Work log history entries cannot be edited

**File:** `maintenance/templates/schedules/detail.html` (Work Log History section)
**Harm:** Work logs are displayed read-only. A user who logged the wrong date, cost, or duration has no recourse. Since logs are immutable by design, a correction would need to be a new log entry — but there's no mechanism for that either and no UI to indicate the old entry is incorrect.
**Fix:** Either allow editing work log entries, or provide a "This entry is incorrect — add a correction" flow. At minimum, the history section should note that entries cannot be changed so users understand the constraint rather than searching for an edit button that doesn't exist.
**Status:** Planned — implement edit/delete actions on work log history table (detail page)

---

### Dashboard grouping is not actionable — only done vs. never done

**File:** `maintenance/templates/dashboard.html`
**Harm:** With a fresh install all 40 schedules land in one "Never Done" bucket, which provides no useful prioritization. Even with history, the dashboard only groups by done/not-done — it doesn't surface overdue or due-soon items in their own prominent section. A homeowner wants to know "what needs attention now," not "what have I ever done."
**Fix:** The overdue and due-soon sections already exist in the template (lines 11-91) but are hidden because no schedules have history. Consider showing the most urgently-needed schedules based on priority and frequency even when never done — e.g. Critical + Annual tasks should appear at the top, not buried in an alphabetical list of 40.
**Status:** Open

---

### Priority, category, and impact not visible on dashboard

**File:** `maintenance/templates/dashboard.html`
**Harm:** The dashboard table shows only Schedule name, Frequency, and Actions. A user looking at 40 tasks has no way to triage which to do first without clicking into each one. A Critical safety task looks identical to a Low cosmetic task.
**Fix:** Add Priority as a column (or at least a small badge/indicator on the schedule name). Category could appear as a subtitle line. This is especially important since the dashboard is the entry point for deciding what to do next.
**Status:** Done — priority badges added to schedule name cell in all dashboard sections (overdue, due_soon, never_done)

---

### Schedule detail: "Details" section uses styled prose, not structured fields

**File:** `maintenance/templates/schedules/detail.html`
**Harm:** Category, Impact, Est. Time, and Notes are displayed as a definition list (`<dt>/<dd>`) which visually resembles indented body text — not recognizable form fields. It's unclear these are editable values or what each one means in the context of scheduling.
**Fix:** Use a consistent card-based metadata layout with clear labels and values, matching the style used elsewhere. Make it visually distinct from free text (the description paragraph).
**Status:** Open

---

### Notes field contains developer instructions, not user content

**Files:** Seed data for schedules (e.g. HVAC humidifier schedule)
**Harm:** The Notes field for some seed schedules contains instructions written for developers configuring the data, not for homeowners using the app — e.g. "Skip this if you don't have a whole-house humidifier. Set active=0." A homeowner reading this is confused: "Set active=0" means nothing to them, and it erodes trust in the app.
**Fix:** Audit all seed schedule Notes fields and rewrite them as user-facing guidance. Developer configuration notes belong in a README or migration comment, not in user-visible content.
**Status:** Open

---

### Frequency (days) and Frequency Label can be set to contradictory values

**File:** Schedule edit form
**Harm:** Nothing prevents a user from setting Frequency = 365 days and Frequency Label = "Quarterly". The label is what's displayed everywhere in the UI, so the schedule will silently use the wrong interval while displaying a misleading label. This is a data integrity hole with no validation.
**Fix:** Either auto-generate the Frequency Label from the day count (removing the manual field), or add server-side validation that the label matches a reasonable interpretation of the day count, or at minimum add a live warning: "Your label says 'Quarterly' but the interval is 365 days (once a year)."
**Status:** Done — replaced with a Frequency model; schedules now pick a shared Frequency instance so label and days are always consistent

---

### Season is not shown on the dashboard or schedule list

**File:** Schedule edit form, dashboard/list templates
**Harm:** The "Season Hint" field exists in the data model but is never surfaced in the main views where it would be most useful — helping a user decide whether now is the right time to do a task. A field with no visible output provides no value to the user filling it in.
**Fix:** Show Season on the schedule list as a lightweight tag or on the dashboard alongside the schedule name. Rename the field "Season" (not "Season Hint") to match what it represents.
**Status:** Done — season_hint shown as a muted subtitle line on dashboard rows and schedule list rows

---

### Cancel button and Save Changes button are mismatched in size

**File:** Schedule edit form
**Harm:** "Save Changes" spans the full form width (~650px); "Cancel" sits beside it as a narrow secondary button. The extreme width disparity makes the layout look broken, and the oversized Save button is visually dominant in a way that draws the eye away from the rest of the form. On mobile both buttons are also reported as too tall.
**Fix:** Constrain both buttons to a consistent width (`width: auto`), align them to the right (or left), and apply the same height via the `filter-actions` class already in use elsewhere. They should be peers, not one dominating the other.
**Status:** Done — `.form-actions` class in CSS sets `width: auto` on both button and anchor; applied to all form templates

---

### Mark Done can be clicked repeatedly with no deduplication

**File:** `maintenance/templates/schedules/detail.html`
**Harm:** Clicking "Mark Done" multiple times in quick succession creates multiple identical work log entries. The button has `hx-disabled-elt="this"` to disable it during the HTMX request, but if the page is reloaded between clicks the protection resets. A user who double-taps or refreshes after logging ends up with duplicate history entries they cannot remove.
**Fix:** Add server-side deduplication: if a work log already exists for this schedule within the last N minutes, reject or warn on a second submission. A lightweight check — `WorkLog.objects.filter(schedule=s, completed_at__gte=now()-timedelta(minutes=5)).exists()` — would catch accidental duplicates.
**Status:** Done — `quick_log()` checks for an existing log within 5 minutes and returns early without creating a duplicate

---

### Purpose of Projects, Issues, and Assets is not explained anywhere

**Files:** `maintenance/templates/projects/list.html`, `maintenance/templates/issues/list.html`, `maintenance/templates/assets/list.html`
**Harm:** A new user sees three empty lists with no explanation of what distinguishes them or when to use each. The subtitles ("One-time improvements, repairs, and upgrades" / "Known problems and things to watch" / "Equipment, systems, and components in your home") are vague. The relationship between them — e.g. an Asset can have a Schedule, an Issue can link to a Project — is invisible.
**Fix:** Add a brief contextual intro to each empty state (2–3 sentences) explaining the use case with a concrete example: "Projects track one-time work like replacing a water heater. Unlike schedules, projects have a start and end. Link an issue to a project to track its resolution."
**Status:** Done — empty states for Projects, Issues, and Assets now include contextual descriptions with concrete examples and relationships

---

### Spending feels disconnected — shows entries with no cost

**File:** `maintenance/templates/spending/` (list/detail views)
**Harm:** The Spending section shows work log entries that have `cost = $0` or `cost = None`, making the list mostly noise. A user who logged "checked smoke detectors" without entering a cost shouldn't see that in the spending history — it provides no financial signal. Similarly, a "Spending by category YTD" breakdown with all-zero costs looks broken.
**Fix:** Filter spending views to only show entries where `cost > 0`. Add a note explaining that cost is optional on work logs and only tracked entries appear here. The summary cards and monthly table should only reflect entries with actual costs.
**Status:** Done — recent logs, category breakdown, and monthly table all filter to `cost__gt=0`; section header updated to "Recent Work Logs with Cost"
