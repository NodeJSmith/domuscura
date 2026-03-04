import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.e2e


def test_dashboard_shows_overdue(page, base_url, seeded_db):
    page.goto(base_url)
    expect(page.locator("text=Clean Gutters")).to_be_visible()


def test_dashboard_shows_never_done(page, base_url, seeded_db):
    page.goto(base_url)
    expect(page.locator("text=Replace HVAC Filter")).to_be_visible()


def test_dashboard_shows_projects(page, base_url, seeded_db):
    page.goto(base_url)
    expect(page.locator("text=Replace Roof")).to_be_visible()


def test_dashboard_quick_done(page, base_url, seeded_db):
    """Click 'Done' on a schedule card and verify the HTMX swap updates status."""
    page.goto(base_url)
    # Find the card for "Replace HVAC Filter" and click its Done button
    card = page.locator(f"#schedule-{seeded_db['schedule'].pk}")
    done_btn = card.get_by_role("button", name="Done")
    done_btn.click()
    # After HTMX swap, the card should show "ok" status indicator
    expect(card.locator(".badge-ok, .status-ok, [data-status='ok']")).to_be_visible(
        timeout=5000
    )
