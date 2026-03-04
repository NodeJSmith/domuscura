from io import StringIO

import pytest
from django.core.management import call_command
from django.db import IntegrityError

from maintenance.management.commands.seed_data import parse_sql_statements
from maintenance.models import Location, Schedule


class TestParseSqlStatements:
    def test_simple_statement(self):
        sql = "SELECT 1;"
        assert parse_sql_statements(sql) == ["SELECT 1"]

    def test_multiple_statements(self):
        sql = "SELECT 1; SELECT 2;"
        assert parse_sql_statements(sql) == ["SELECT 1", "SELECT 2"]

    def test_handles_comments(self):
        sql = "-- comment\nSELECT 1;"
        stmts = parse_sql_statements(sql)
        assert stmts == ["SELECT 1"]

    def test_handles_quoted_strings(self):
        sql = "INSERT INTO t VALUES ('hello; world');"
        stmts = parse_sql_statements(sql)
        assert len(stmts) == 1
        assert "hello; world" in stmts[0]

    def test_handles_escaped_quotes(self):
        sql = "INSERT INTO t VALUES ('it''s a test');"
        stmts = parse_sql_statements(sql)
        assert len(stmts) == 1
        assert "it''s a test" in stmts[0]

    def test_handles_comment_in_middle(self):
        sql = "SELECT 1; -- comment\nSELECT 2;"
        stmts = parse_sql_statements(sql)
        assert stmts == ["SELECT 1", "SELECT 2"]

    def test_empty_input(self):
        assert parse_sql_statements("") == []

    def test_no_trailing_semicolon(self):
        sql = "SELECT 1"
        stmts = parse_sql_statements(sql)
        assert stmts == ["SELECT 1"]

    def test_whitespace_only(self):
        assert parse_sql_statements("   \n\n  ") == []


class TestSeedDataCommand:
    def test_seed_data_loads(self, db):
        out = StringIO()
        call_command("seed_data", stdout=out)
        output = out.getvalue()
        assert "Loaded" in output
        assert Location.objects.count() > 0
        assert Schedule.objects.count() > 0

    def test_seed_data_idempotent(self, db):
        call_command("seed_data")
        initial_locs = Location.objects.count()

        out = StringIO()
        call_command("seed_data", stdout=out)
        output = out.getvalue()
        assert "already" in output.lower()
        assert Location.objects.count() == initial_locs

    @pytest.mark.django_db(transaction=True)
    def test_seed_data_force_bypasses_guard(self):
        """With --force, the command skips the 'already loaded' check."""
        # First, create a location so the guard would normally trigger
        Location.objects.create(name="Pre-existing")
        assert Location.objects.exists()

        out = StringIO()
        # Force will attempt to load, but will hit unique constraint on
        # locations — we just verify it got past the guard (no "already" msg)
        try:
            call_command("seed_data", "--force", stdout=out, stderr=StringIO())
        except IntegrityError:
            pass
        output = out.getvalue()
        assert "already" not in output.lower()
