import pytest
from django.test import Client
from django.urls import reverse

from maintenance.models import Issue


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def resolved_issue(db, location):
    return Issue.objects.create(
        summary="Fixed leak",
        location=location,
        severity="minor",
        status="resolved",
    )


class TestIssueList:
    def test_list_loads(self, client, db):
        resp = client.get(reverse("issue_list"))
        assert resp.status_code == 200

    def test_list_active_by_default(self, client, issue, resolved_issue):
        resp = client.get(reverse("issue_list"))
        summaries = [i.summary for i in resp.context["issues"]]
        assert "Cracked foundation wall" in summaries
        assert "Fixed leak" not in summaries

    def test_list_filter_by_status(self, client, issue, resolved_issue):
        resp = client.get(reverse("issue_list"), {"status": "resolved"})
        summaries = [i.summary for i in resp.context["issues"]]
        assert "Fixed leak" in summaries
        assert "Cracked foundation wall" not in summaries

    def test_list_filter_by_severity(self, client, issue):
        resp = client.get(reverse("issue_list"), {"severity": "major"})
        assert len(resp.context["issues"]) == 1

        resp = client.get(reverse("issue_list"), {"severity": "cosmetic"})
        assert len(resp.context["issues"]) == 0

    def test_list_filter_by_search(self, client, issue):
        resp = client.get(reverse("issue_list"), {"q": "foundation"})
        assert len(resp.context["issues"]) == 1

        resp = client.get(reverse("issue_list"), {"q": "nonexistent"})
        assert len(resp.context["issues"]) == 0

    def test_list_show_all_statuses(self, client, issue, resolved_issue):
        """status="" shows everything (no filter)."""
        resp = client.get(reverse("issue_list"), {"status": ""})
        assert len(resp.context["issues"]) == 2


class TestIssueDetail:
    def test_detail_loads(self, client, issue):
        resp = client.get(reverse("issue_detail", args=[issue.pk]))
        assert resp.status_code == 200
        assert resp.context["issue"].summary == "Cracked foundation wall"

    def test_detail_404(self, client, db):
        resp = client.get(reverse("issue_detail", args=[99999]))
        assert resp.status_code == 404


class TestIssueCreate:
    def test_create_get(self, client, db):
        resp = client.get(reverse("issue_create"))
        assert resp.status_code == 200
        assert resp.context["editing"] is False

    def test_create_post_valid(self, client, db):
        resp = client.post(reverse("issue_create"), {
            "summary": "New Issue",
            "severity": "minor",
            "status": "open",
        })
        assert resp.status_code == 302
        assert Issue.objects.filter(summary="New Issue").exists()

    def test_create_post_invalid(self, client, db):
        resp = client.post(reverse("issue_create"), {"summary": ""})
        assert resp.status_code == 200


class TestIssueEdit:
    def test_edit_get(self, client, issue):
        resp = client.get(reverse("issue_edit", args=[issue.pk]))
        assert resp.status_code == 200
        assert resp.context["editing"] is True

    def test_edit_post_valid(self, client, issue):
        resp = client.post(reverse("issue_edit", args=[issue.pk]), {
            "summary": "Updated Issue",
            "severity": "safety",
            "status": "monitoring",
        })
        assert resp.status_code == 302
        issue.refresh_from_db()
        assert issue.summary == "Updated Issue"
        assert issue.severity == "safety"

    def test_edit_404(self, client, db):
        resp = client.get(reverse("issue_edit", args=[99999]))
        assert resp.status_code == 404
