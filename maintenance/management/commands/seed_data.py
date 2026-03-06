import sqlite3
from pathlib import Path

from django.core.management.base import BaseCommand

from maintenance.models import Category, Frequency, Location, Schedule

BASE_PATH = Path(__file__).resolve().parents[3]


def parse_sql_statements(sql):
    """Split SQL into individual statements, handling quotes and comments."""
    statements = []
    current = []
    i = 0
    while i < len(sql):
        c = sql[i]
        # Skip -- line comments (apostrophes in comments break quote tracking)
        if c == "-" and i + 1 < len(sql) and sql[i + 1] == "-":
            while i < len(sql) and sql[i] != "\n":
                i += 1
            continue
        # Handle quoted strings (with '' escaping)
        if c == "'":
            current.append(c)
            i += 1
            while i < len(sql):
                if sql[i] == "'" and i + 1 < len(sql) and sql[i + 1] == "'":
                    current.append("''")
                    i += 2
                elif sql[i] == "'":
                    current.append("'")
                    i += 1
                    break
                else:
                    current.append(sql[i])
                    i += 1
        elif c == ";":
            stmt = "".join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
            i += 1
        else:
            current.append(c)
            i += 1

    leftover = "".join(current).strip()
    if leftover:
        statements.append(leftover)

    return statements


class Command(BaseCommand):
    help = "Load seed data (locations and maintenance schedules) from the SQL file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Load seed data even if data already exists",
        )

    def handle(self, *args, **options):
        if not options["force"] and Location.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Seed data appears to already be loaded (locations exist). "
                    "Use --force to reload."
                )
            )
            return

        schema_file = BASE_PATH / "home_maintenance_schema_v2.sql"
        seed_file = BASE_PATH / "home_maintenance_seed_data_v2.sql"

        for f in (schema_file, seed_file):
            if not f.exists():
                self.stderr.write(self.style.ERROR(f"File not found: {f}"))
                return

        # Load seed data into a temporary in-memory SQLite database
        # using the original schema (with proper DEFAULT values).
        tmp = sqlite3.connect(":memory:")
        tmp.row_factory = sqlite3.Row
        tmp.executescript(schema_file.read_text())

        # Use our custom parser for seed data (handles '' escaped quotes
        # that contain semicolons inside string values).
        for stmt in parse_sql_statements(seed_file.read_text()):
            lines = [line for line in stmt.splitlines() if line.strip() and not line.strip().startswith("--")]
            if not lines:
                continue
            tmp.execute(stmt)

        tmp.commit()

        # Copy locations via Django ORM
        for row in tmp.execute("SELECT name, notes FROM locations"):
            Location.objects.create(name=row["name"], notes=row["notes"] or "")

        # Copy schedules via Django ORM
        for row in tmp.execute(
            """
            SELECT name, description, category, frequency_days, frequency_label,
                   priority, impact, estimated_minutes, estimated_cost,
                   pro_recommended, active, notes
            FROM schedules
            """
        ):
            frequency, _ = Frequency.objects.get_or_create(
                days=row["frequency_days"],
                defaults={"label": row["frequency_label"] or ""},
            )
            category = None
            if row["category"]:
                category, _ = Category.objects.get_or_create(name=row["category"])
            Schedule.objects.create(
                name=row["name"],
                description=row["description"] or "",
                category=category,
                frequency=frequency,
                priority=row["priority"] or "normal",
                impact=row["impact"] or "",
                estimated_minutes=row["estimated_minutes"],
                estimated_cost=row["estimated_cost"],
                pro_recommended=bool(row["pro_recommended"]),
                active=bool(row["active"]) if row["active"] is not None else True,
                notes=row["notes"] or "",
            )

        tmp.close()

        location_count = Location.objects.count()
        schedule_count = Schedule.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded {location_count} locations and {schedule_count} schedules."
            )
        )
