# Changelog

All notable changes to Domuscura are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Responsive CSS: schedule card grids now wrap instead of cramming into a single unreadable row (#2)
- Responsive tables: list views scroll horizontally on narrow viewports instead of overflowing (#2)
- `ScheduleStatus` named tuple — `Schedule.compute_status()` is now a pure function with no side effects (#2)

### Changed
- Type annotations added to all view functions, model methods, and form methods (#2)

### Fixed
- Failed HTMX requests now show an error toast instead of silently ignoring errors
- Work-log modal can be dismissed by clicking the backdrop
- Submit buttons are disabled during in-flight HTMX requests, preventing duplicate submissions
- Detail-page related tables (assets, projects) now scroll horizontally on narrow viewports
- Touch targets on action and card buttons enlarged for usability
- Major severity badge contrast ratio fixed (was ~3.3:1, now ~6.6:1, passes WCAG AA)
- Forms now display a "Fields marked * are required" legend

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
