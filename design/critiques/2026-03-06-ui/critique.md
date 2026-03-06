# UI Design Critique — 2026-03-06

Three-critic adversarial review of the full Domuscura UI (templates + CSS).
Critics: Skeptical Senior Engineer · Systems Architect · Adversarial Reviewer

---

## CRITICAL findings (all 3 critics)

### Sort links drop the `location` filter — active data-loss bug
**Fixed in this session.**
Every column-sort anchor in `schedules/list.html:87-91` omitted `&location=`. Clicking any sort header while a location filter was active silently cleared it.
**Fix:** Added `&location={{ filters.location }}` to all five sort hrefs.

### `quick_log` has three incompatible callers — returns invalid HTML to table context
**Fixed in this session.**
`quick_log` always returned `schedule_card.html` (an `<article>`, `id="schedule-{id}"`). The schedule list's Done button targeted `#schedule-row-{id}` — ID mismatch, HTMX did nothing, duplicate work logs created on re-click.
**Fix:** View now checks `HX-Target` header; returns `schedule_row.html` when target starts with `schedule-row-`.

### Work log modal copy-pasted verbatim — duplicate IDs across pages
**Fixed in this session.**
`dashboard.html:216-232` and `schedules/list.html:103-120` were byte-for-byte copies, both declaring `id="work-log-modal"` and `id="work-log-form-container"`.
**Fix:** Extracted to `partials/work_log_modal.html`, both pages now use `{% include %}`.

### `performed_by` hardcoded `"self"` — guaranteed unqueryable data
**Fixed in this session.**
`quick_log` stamped `performed_by="self"` on every entry; the work log form accepted free text. Two code paths, two data formats, one unusable field.
**Fix:** `performed_by=request.user.get_full_name() or request.user.username`.

---

## HIGH findings (2 critics)

### Race condition: two HTMX GETs fire simultaneously on "Log Work" click
**Fixed in this session.**
`#work-log-form-container` carried its own `hx-get` + `hx-trigger="work-log-open from:window"` racing against the button's own `hx-get`. On slow connections the generic form won — user submitted with no schedule attached.
**Fix:** Removed `hx-get` and `hx-trigger` from `#work-log-form-container` in `partials/work_log_modal.html`. The container is now a passive target; each "Log Work" button owns its own form load.

### Unconditional reload fires on errors, destroying the toast
**Fixed in this session.**
`schedules/detail.html` used `hx-on::after-request="window.location.reload()"` with no success guard. On 403/500, the page reloaded immediately, destroying the error toast.
**Fix:** `if(event.detail.successful) window.location.reload()`

### Hardcoded hex colors fail WCAG AA in dark mode
**Fixed in this session.**
`#e67e22` and `#b35c00` defined as `--color-warning` and `--color-severity-major` in `app.css` with `@media (prefers-color-scheme: dark)` overrides. All three hardcoded values replaced with `var()` references in `status_badge.html`, `schedules/detail.html`, `issues/list.html`.

### Filter architecture inconsistent across list pages
**Fixed in this session.**
Removed `hx-get`, `hx-target`, `hx-push-url`, `hx-sync` from the schedule filter form. All list pages now use plain `method="get"`. Side effect: stale count bug (MEDIUM) eliminated — full page render always shows accurate count.

### `status_badge` silently renders nothing for unrecognized statuses
**Fixed in this session.**
Added `{% elif status %}<mark>{{ status }}</mark>{% endif %}` fallback. Unknown statuses now render as unstyled badges rather than invisibly.

---

## MEDIUM findings (1 critic)

| Finding | File | Fix |
|---------|------|-----|
| HTMX filter leaves count stale after filtering | `schedules/list.html:95-101` | Expand HTMX target to include count element |
| `<details open>` default-expanded filters invert page priority | `schedules/list.html:12`, `issues/list.html:11` | Default collapsed, persist state to localStorage |
| `<mark>` is semantically wrong for status badges | `status_badge.html:1-15` | Use `<span class="badge badge--overdue">` with CSS |
| Double full-table scan per request for category dropdown | `views/schedule.py:95-98` | Derive categories from already-filtered queryset |
| `loc.id|slugify` comparison is accidental correctness | `schedules/list.html:50` | Use `|stringformat:"s"` instead |

---

## Appendix: Individual critic reports

These files contain each critic's unfiltered findings:

- Senior Engineer: `/tmp/mine-challenge-senior-critique.md`
- Systems Architect: `/tmp/mine-challenge-architect-critique.md`
- Adversarial Reviewer: `/tmp/mine-challenge-adversarial-critique.md`
