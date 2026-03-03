from datetime import timedelta
from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from maintenance.models import Schedule, WorkLog


@pytest.fixture
def client():
    return Client()


class TestSpendingSummary:
    def test_spending_loads_empty(self, client, db):
        resp = client.get(reverse("spending_summary"))
        assert resp.status_code == 200
        assert resp.context["stats"]["all_time"]["total_cost"] == 0
        assert resp.context["stats"]["all_time"]["total_entries"] == 0

    def test_spending_with_work_logs(self, client, work_log):
        resp = client.get(reverse("spending_summary"))
        stats = resp.context["stats"]
        assert stats["all_time"]["total_cost"] == Decimal("25.00")
        assert stats["all_time"]["total_entries"] == 1
        assert stats["all_time"]["total_minutes"] == 20

    def test_spending_time_periods(self, client, db, schedule):
        # Create a log from 60 days ago
        WorkLog.objects.create(
            schedule=schedule,
            completed_at=timezone.now() - timedelta(days=60),
            cost=Decimal("100.00"),
            performed_by="self",
        )
        # Create a log from today
        WorkLog.objects.create(
            schedule=schedule,
            completed_at=timezone.now(),
            cost=Decimal("50.00"),
            performed_by="self",
        )

        resp = client.get(reverse("spending_summary"))
        stats = resp.context["stats"]

        # Both should be in all_time
        assert stats["all_time"]["total_cost"] == Decimal("150.00")
        assert stats["all_time"]["total_entries"] == 2

        # Only today's should be in last_30
        assert stats["last_30"]["total_cost"] == Decimal("50.00")

    def test_spending_categories(self, client, work_log, schedule):
        resp = client.get(reverse("spending_summary"))
        categories = resp.context["categories"]
        assert len(categories) >= 1
        assert categories[0]["name"] == "HVAC"

    def test_spending_recent_logs(self, client, work_log):
        resp = client.get(reverse("spending_summary"))
        assert len(resp.context["recent_logs"]) == 1

    def test_spending_months(self, client, db):
        resp = client.get(reverse("spending_summary"))
        assert len(resp.context["months"]) == 12
