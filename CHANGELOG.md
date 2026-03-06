# Changelog

All notable changes to Domuscura are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Changed
- "Done" button replaced by "Log Work" modal on dashboard and schedule list — logging work now always records cost, duration, and notes rather than creating a bare timestamp entry

### Added
- Schedule frequencies are now a reusable model — create and manage intervals (Weekly, Monthly, Annually, etc.) from a dedicated Frequencies page; schedules pick one from the list
- Schedule form: preset picker (Weekly / Monthly / Annually / etc.) auto-fills frequency fields — no more mental arithmetic
- Spending page: empty state explanation when no costs have been recorded yet
- Schedule detail: "Log Work with Details" button in status card when a schedule has never been completed

### Fixed
- New Issue form: Discovered Date now defaults to today instead of blank
- Work log form: "Completed on" is now a simple date picker — no time-of-day required
- Schedule detail: duplicate Impact row hidden when it matches the Category
- Schedule edit form: helper text added for Impact, Season Hint, and Professional Recommended fields

### Added
- Responsive CSS: schedule card grids now wrap instead of cramming into a single unreadable row (#2)
- Responsive tables: list views scroll horizontally on narrow viewports instead of overflowing (#2)
- `ScheduleStatus` named tuple — `Schedule.compute_status()` is now a pure function with no side effects (#2)

### Changed
- Type annotations added to all view functions, model methods, and form methods (#2)

### Fixed
- "Done" button now shows a confirmation dialog before creating a work log
- Duplicate quick-logs within 5 minutes are silently ignored server-side
- Log Work modal Save button is now always visible (sticky footer, scrollable form)
- Duration field in Log Work modal pre-fills from the schedule's estimated time
- Dropdown empty labels now use natural language ("No specific asset", "Unspecified", etc.) instead of "---------"
- Schedule detail subtitle no longer reads "Annually interval" — frequency labels stand alone
- Failed HTMX requests now show an error toast instead of silently ignoring errors
- Work-log modal can be dismissed by clicking the backdrop
- Submit buttons are disabled during in-flight HTMX requests, preventing duplicate submissions
- Detail-page related tables (assets, projects) now scroll horizontally on narrow viewports
- Touch targets on action and card buttons enlarged to 44px minimum for usability
- Major severity badge contrast ratio fixed (was ~3.3:1, now ~6.6:1, passes WCAG AA)
- Forms now display a "Fields marked * are required" legend
- Dark mode now respects system preference (removed forced light theme)
- Empty Issues/Projects/Assets pages now show onboarding links instead of misleading "no results" message
- Active nav link is underlined so current section is always visible
- Dashboard schedule groups now expand by default instead of collapsing on first visit
- Filter action buttons (Filter / Clear / + New) are now compact and properly sized
- Schedule list hides secondary columns (Category, Frequency, Priority) on narrow mobile screens
- "Mark Done" button on schedule detail page now disables during the request to prevent duplicate logs

---

## [0.1.0] — 2026-03-03

Initial release.

### Added
- Recurring schedule tracking with overdue/due-soon/ok status computation
- Project management with status lifecycle (someday → pending → in-progress → done)
- Issue tracking with severity levels
- Asset registry with warranty and age tracking
- Spending dashboard with monthly and category breakdowns
- Work log history (immutable, linked to schedules or projects)
- HTMX-powered partial updates and Alpine.js modal for work logging
- Docker + CI/CD pipeline with Playwright e2e tests
- Seed data: ~40 common home maintenance schedules

[Unreleased]: https://github.com/NodeJSmith/domuscura/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/NodeJSmith/domuscura/releases/tag/v0.1.0
