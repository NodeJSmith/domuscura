-- =============================================================================
-- Home Maintenance Tracker v2 - SQLite Schema for Hassette
-- =============================================================================
-- Designed for SQLite WAL mode. All timestamps stored as ISO 8601 UTC strings.
--
-- Key design change from v1: recurring schedules, one-off projects, and
-- known issues are separate tables instead of being shoe-horned into one
-- overloaded task_definitions table.
--
-- Seven tables:
--   locations     — zones/areas of the home
--   assets        — the physical things you own and maintain
--   schedules     — recurring maintenance templates (the "do X every Y days")
--   projects      — one-off and someday work items
--   issues        — observations about condition/quality of things
--   work_log      — history of completed work (links to schedules OR projects)
--   documents     — file attachments (links to assets, work_log, issues, or projects)

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- =============================================================================
-- CORE TABLES
-- =============================================================================

-- Locations/zones in the home
CREATE TABLE IF NOT EXISTS locations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,          -- "Kitchen", "Basement", "Exterior - North"
    notes       TEXT,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- Assets: the physical things you maintain
CREATE TABLE IF NOT EXISTS assets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,             -- "Furnace", "Water Heater", "Roof"
    location_id     INTEGER,
    category        TEXT,                      -- "HVAC", "Plumbing", "Electrical", "Exterior", "Appliance", "Safety", "Structural"
    make            TEXT,
    model           TEXT,
    serial_number   TEXT,
    install_date    TEXT,                      -- ISO date
    warranty_expires TEXT,                     -- ISO date
    expected_lifespan_years INTEGER,
    purchase_price  REAL,
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
);

-- =============================================================================
-- RECURRING MAINTENANCE
-- =============================================================================

-- Schedules: recurring maintenance templates
-- ONLY for things that repeat on an interval. Clean and focused.
CREATE TABLE IF NOT EXISTS schedules (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL,             -- "Replace HVAC air filter"
    description         TEXT,                      -- detailed instructions
    asset_id            INTEGER,                   -- NULL = general task not tied to specific asset
    location_id         INTEGER,                   -- for tasks not tied to an asset (e.g. "inspect foundation")
    category            TEXT,                      -- "HVAC", "Plumbing", etc. Used when asset_id is NULL; otherwise prefer asset's category
    frequency_days      INTEGER NOT NULL,          -- interval in days (30, 90, 180, 365, etc.)
    frequency_label     TEXT,                      -- human-readable: "Monthly", "Quarterly", etc.
    season_hint         TEXT,                      -- "spring", "fall", "spring,fall", NULL for any time
    priority            TEXT DEFAULT 'normal',     -- "low", "normal", "high", "critical"
    impact              TEXT,                      -- "safety", "protective", "efficiency", "cosmetic", "comfort"
    estimated_minutes   INTEGER,
    estimated_cost      REAL,
    pro_recommended     INTEGER DEFAULT 0,
    active              INTEGER DEFAULT 1,         -- 0 to pause schedules that don't apply
    notes               TEXT,
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE SET NULL,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
);

-- =============================================================================
-- ONE-OFF WORK
-- =============================================================================

-- Projects: planned one-off work items (including someday/wish list)
-- This is your to-do list for the house. Not recurring.
CREATE TABLE IF NOT EXISTS projects (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL,             -- "Replace front door"
    description         TEXT,
    asset_id            INTEGER,
    location_id         INTEGER,
    category            TEXT,                      -- "HVAC", "Plumbing", "Interior", "Exterior", etc.
    priority            TEXT DEFAULT 'normal',     -- "low", "normal", "high", "critical"
    impact              TEXT,                      -- "safety", "protective", "efficiency", "cosmetic", "comfort"
    status              TEXT DEFAULT 'pending',    -- "someday", "pending", "in_progress", "done", "cancelled"
    target_date         TEXT,                      -- optional deadline (ISO date)
    estimated_cost      REAL,
    pro_recommended     INTEGER DEFAULT 0,
    completed_at        TEXT,                      -- when it was finished
    notes               TEXT,
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE SET NULL,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
);

-- =============================================================================
-- OBSERVATIONS
-- =============================================================================

-- Issues: known conditions, defects, observations
-- Not action items — these describe the STATE of things.
-- Can optionally link to a project if you decide to act on it.
CREATE TABLE IF NOT EXISTS issues (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    summary         TEXT NOT NULL,              -- "Garage door not installed properly"
    details         TEXT,
    asset_id        INTEGER,
    location_id     INTEGER,                   -- for issues not tied to a specific asset
    severity        TEXT DEFAULT 'minor',       -- "cosmetic", "minor", "moderate", "major", "safety"
    status          TEXT DEFAULT 'open',        -- "open", "monitoring", "accepted", "scheduled", "resolved"
    source          TEXT,                       -- "self", "home_inspector", "contractor"
    discovered_at   TEXT,
    resolved_at     TEXT,
    project_id      INTEGER,                   -- link to project when you decide to fix it
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE SET NULL,
    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- =============================================================================
-- HISTORY
-- =============================================================================

-- Work log: records of completed work
-- Links to EITHER a schedule (recurring) OR a project (one-off), or neither (ad-hoc).
-- For recurring tasks, this is where interval tracking comes from.
-- For projects, this captures cost/notes/who-did-it details on completion.
CREATE TABLE IF NOT EXISTS work_log (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id         INTEGER,               -- which recurring schedule this fulfills
    project_id          INTEGER,               -- which project this fulfills
    asset_id            INTEGER,               -- for ad-hoc work not tied to a schedule or project
    completed_at        TEXT NOT NULL,          -- when the work was done
    performed_by        TEXT,                   -- "self", contractor name, etc.
    cost                REAL DEFAULT 0,
    duration_minutes    INTEGER,
    notes               TEXT,
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (schedule_id) REFERENCES schedules(id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE SET NULL,
    -- At least one context should be set, but enforced in app logic, not here.
    -- A work_log entry with all three NULL is an orphaned ad-hoc record (still valid).
    CHECK (NOT (schedule_id IS NOT NULL AND project_id IS NOT NULL))  -- can't be both
);

-- =============================================================================
-- ATTACHMENTS
-- =============================================================================

-- Documents: receipts, warranties, manuals, photos
-- Can link to any combination of: asset, work_log entry, issue, or project.
-- Typically attached to just one, but not enforced (e.g. a warranty PDF might
-- belong on both the asset and the work_log entry where it was referenced).
CREATE TABLE IF NOT EXISTS documents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id        INTEGER,
    work_log_id     INTEGER,
    issue_id        INTEGER,
    project_id      INTEGER,
    filename        TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    doc_type        TEXT,                      -- "receipt", "warranty", "manual", "photo", "invoice", "estimate", "other"
    description     TEXT,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE SET NULL,
    FOREIGN KEY (work_log_id) REFERENCES work_log(id) ON DELETE SET NULL,
    FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- =============================================================================
-- VIEWS
-- =============================================================================

-- Dashboard: recurring schedule status
CREATE VIEW IF NOT EXISTS v_schedule_status AS
SELECT
    s.id AS schedule_id,
    s.name,
    s.frequency_days,
    s.frequency_label,
    s.season_hint,
    s.priority,
    s.impact,
    s.pro_recommended,
    s.estimated_cost,
    a.name AS asset_name,
    COALESCE(s.category, a.category) AS category,
    COALESCE(s.location_id, a.location_id) AS effective_location_id,
    loc.name AS location_name,
    last_log.last_completed,
    last_log.last_notes,
    CASE
        WHEN last_log.last_completed IS NULL THEN 'never_done'
        WHEN julianday('now') - julianday(last_log.last_completed) > s.frequency_days THEN 'overdue'
        WHEN julianday('now') - julianday(last_log.last_completed) > (s.frequency_days * 0.85) THEN 'due_soon'
        ELSE 'ok'
    END AS status,
    CASE
        WHEN last_log.last_completed IS NULL THEN NULL
        ELSE CAST(julianday('now') - julianday(last_log.last_completed) AS INTEGER)
    END AS days_since_last,
    CASE
        WHEN last_log.last_completed IS NULL THEN NULL
        ELSE date(julianday(last_log.last_completed) + s.frequency_days)
    END AS next_due_date
FROM schedules s
LEFT JOIN assets a ON s.asset_id = a.id
LEFT JOIN locations loc ON COALESCE(s.location_id, a.location_id) = loc.id
LEFT JOIN (
    SELECT
        schedule_id,
        MAX(completed_at) AS last_completed,
        (SELECT notes FROM work_log wl2
         WHERE wl2.schedule_id = wl.schedule_id
         ORDER BY completed_at DESC LIMIT 1) AS last_notes
    FROM work_log wl
    WHERE wl.schedule_id IS NOT NULL
    GROUP BY schedule_id
) last_log ON s.id = last_log.schedule_id
WHERE s.active = 1
ORDER BY
    CASE
        WHEN last_log.last_completed IS NULL THEN 0
        WHEN julianday('now') - julianday(last_log.last_completed) > s.frequency_days THEN 1
        WHEN julianday('now') - julianday(last_log.last_completed) > (s.frequency_days * 0.85) THEN 2
        ELSE 3
    END,
    next_due_date ASC;

-- Active projects (excludes done/cancelled)
CREATE VIEW IF NOT EXISTS v_active_projects AS
SELECT
    p.id AS project_id,
    p.name,
    p.category,
    p.priority,
    p.impact,
    p.status,
    p.target_date,
    p.estimated_cost,
    p.pro_recommended,
    a.name AS asset_name,
    loc.name AS location_name,
    CASE
        WHEN p.status = 'someday' THEN 'someday'
        WHEN p.target_date IS NOT NULL AND p.target_date < date('now') THEN 'overdue'
        WHEN p.target_date IS NOT NULL AND julianday(p.target_date) - julianday('now') <= 14 THEN 'due_soon'
        ELSE p.status
    END AS effective_status,
    (SELECT COUNT(*) FROM issues i WHERE i.project_id = p.id AND i.status != 'resolved') AS linked_issues
FROM projects p
LEFT JOIN assets a ON p.asset_id = a.id
LEFT JOIN locations loc ON COALESCE(p.location_id, a.location_id) = loc.id
WHERE p.status NOT IN ('done', 'cancelled')
ORDER BY
    CASE p.priority
        WHEN 'critical' THEN 0
        WHEN 'high' THEN 1
        WHEN 'normal' THEN 2
        WHEN 'low' THEN 3
    END,
    CASE WHEN p.status = 'someday' THEN 1 ELSE 0 END,
    CASE WHEN p.target_date IS NULL THEN 1 ELSE 0 END,
    p.target_date ASC;

-- Open issues by severity
CREATE VIEW IF NOT EXISTS v_open_issues AS
SELECT
    i.id AS issue_id,
    i.summary,
    i.details,
    i.severity,
    i.status,
    i.source,
    i.discovered_at,
    a.name AS asset_name,
    a.category AS asset_category,
    loc.name AS location_name,
    p.name AS linked_project_name,
    p.status AS linked_project_status
FROM issues i
LEFT JOIN assets a ON i.asset_id = a.id
LEFT JOIN locations loc ON COALESCE(i.location_id, a.location_id) = loc.id
LEFT JOIN projects p ON i.project_id = p.id
WHERE i.status != 'resolved'
ORDER BY
    CASE i.severity
        WHEN 'safety' THEN 0
        WHEN 'major' THEN 1
        WHEN 'moderate' THEN 2
        WHEN 'minor' THEN 3
        WHEN 'cosmetic' THEN 4
    END,
    i.discovered_at ASC;

-- Spending log (individual entries, filter/aggregate in app as needed)
CREATE VIEW IF NOT EXISTS v_spending_log AS
SELECT
    strftime('%Y', wl.completed_at) AS year,
    COALESCE(
        s.name,
        p.name,
        'Ad-hoc: ' || COALESCE(a.name, 'Unknown')
    ) AS work_name,
    CASE
        WHEN s.id IS NOT NULL THEN 'recurring'
        WHEN p.id IS NOT NULL THEN 'project'
        ELSE 'ad_hoc'
    END AS work_type,
    COALESCE(s.category, a.category, p.category, 'Uncategorized') AS category,
    wl.cost,
    wl.completed_at
FROM work_log wl
LEFT JOIN schedules s ON wl.schedule_id = s.id
LEFT JOIN projects p ON wl.project_id = p.id
LEFT JOIN assets a ON COALESCE(s.asset_id, p.asset_id, wl.asset_id) = a.id
WHERE wl.cost > 0
ORDER BY wl.completed_at DESC;

-- Asset age and replacement timeline
CREATE VIEW IF NOT EXISTS v_asset_lifecycle AS
SELECT
    a.id,
    a.name,
    a.category,
    a.install_date,
    a.expected_lifespan_years,
    a.warranty_expires,
    l.name AS location_name,
    CASE
        WHEN a.install_date IS NOT NULL
        THEN CAST((julianday('now') - julianday(a.install_date)) / 365.25 AS INTEGER)
    END AS age_years,
    CASE
        WHEN a.install_date IS NOT NULL AND a.expected_lifespan_years IS NOT NULL
        THEN date(julianday(a.install_date) + (a.expected_lifespan_years * 365.25))
    END AS estimated_replacement_date,
    CASE
        WHEN a.warranty_expires IS NOT NULL AND a.warranty_expires < date('now')
        THEN 'expired'
        WHEN a.warranty_expires IS NOT NULL
        THEN 'active'
        ELSE 'unknown'
    END AS warranty_status,
    (SELECT COUNT(*) FROM issues i WHERE i.asset_id = a.id AND i.status != 'resolved') AS open_issues
FROM assets a
LEFT JOIN locations l ON a.location_id = l.id
ORDER BY estimated_replacement_date ASC;

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_work_log_completed ON work_log(completed_at);
CREATE INDEX IF NOT EXISTS idx_work_log_schedule ON work_log(schedule_id);
CREATE INDEX IF NOT EXISTS idx_work_log_project ON work_log(project_id);
CREATE INDEX IF NOT EXISTS idx_schedules_asset ON schedules(asset_id);
CREATE INDEX IF NOT EXISTS idx_schedules_active ON schedules(active);
CREATE INDEX IF NOT EXISTS idx_schedules_category ON schedules(category);
CREATE INDEX IF NOT EXISTS idx_schedules_impact ON schedules(impact);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_priority ON projects(priority);
CREATE INDEX IF NOT EXISTS idx_projects_impact ON projects(impact);
CREATE INDEX IF NOT EXISTS idx_assets_category ON assets(category);
CREATE INDEX IF NOT EXISTS idx_documents_asset ON documents(asset_id);
CREATE INDEX IF NOT EXISTS idx_documents_work_log ON documents(work_log_id);
CREATE INDEX IF NOT EXISTS idx_documents_issue ON documents(issue_id);
CREATE INDEX IF NOT EXISTS idx_documents_project ON documents(project_id);
CREATE INDEX IF NOT EXISTS idx_issues_asset ON issues(asset_id);
CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);
CREATE INDEX IF NOT EXISTS idx_issues_project ON issues(project_id);
