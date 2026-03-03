import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.e2e


def test_dashboard_loads(page, base_url, seeded_db):
    page.goto(base_url)
    expect(page).to_have_title("Domuscura", timeout=5000)


def test_nav_to_schedules(page, base_url, seeded_db):
    page.goto(base_url)
    page.get_by_role("link", name="Schedules").click()
    expect(page).to_have_url(f"{base_url}/schedules/")
    expect(page.locator("h1")).to_contain_text("Schedules")


def test_nav_to_projects(page, base_url, seeded_db):
    page.goto(base_url)
    page.get_by_role("link", name="Projects").click()
    expect(page).to_have_url(f"{base_url}/projects/")


def test_nav_to_issues(page, base_url, seeded_db):
    page.goto(base_url)
    page.get_by_role("link", name="Issues").click()
    expect(page).to_have_url(f"{base_url}/issues/")


def test_nav_to_assets(page, base_url, seeded_db):
    page.goto(base_url)
    page.get_by_role("link", name="Assets").click()
    expect(page).to_have_url(f"{base_url}/assets/")


def test_nav_to_spending(page, base_url, seeded_db):
    page.goto(base_url)
    page.get_by_role("link", name="Spending").click()
    expect(page).to_have_url(f"{base_url}/spending/")
