import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.e2e


def test_project_crud(page, base_url, seeded_db):
    # Create
    page.goto(f"{base_url}/projects/new/")
    page.locator("input[name='name']").fill("E2E Test Project")
    page.locator("select[name='priority']").select_option("high")
    page.locator("select[name='status']").select_option("pending")
    page.get_by_role("button", name="Save").click()
    expect(page.locator("text=E2E Test Project")).to_be_visible()

    # Edit
    page.get_by_role("link", name="Edit").click()
    page.locator("input[name='name']").fill("E2E Updated Project")
    page.get_by_role("button", name="Save").click()
    expect(page.locator("text=E2E Updated Project")).to_be_visible()


def test_issue_crud(page, base_url, seeded_db):
    # Create
    page.goto(f"{base_url}/issues/new/")
    page.locator("input[name='summary']").fill("E2E Test Issue")
    page.locator("select[name='severity']").select_option("minor")
    page.get_by_role("button", name="Save").click()
    expect(page.locator("text=E2E Test Issue")).to_be_visible()

    # Edit
    page.get_by_role("link", name="Edit").click()
    page.locator("input[name='summary']").fill("E2E Updated Issue")
    page.get_by_role("button", name="Save").click()
    expect(page.locator("text=E2E Updated Issue")).to_be_visible()


def test_asset_crud(page, base_url, seeded_db):
    # Create
    page.goto(f"{base_url}/assets/new/")
    page.locator("input[name='name']").fill("E2E Test Asset")
    page.get_by_role("button", name="Save").click()
    expect(page.locator("text=E2E Test Asset")).to_be_visible()

    # Edit
    page.get_by_role("link", name="Edit").click()
    page.locator("input[name='name']").fill("E2E Updated Asset")
    page.get_by_role("button", name="Save").click()
    expect(page.locator("text=E2E Updated Asset")).to_be_visible()


def test_spending_page_loads(page, base_url, seeded_db):
    page.goto(f"{base_url}/spending/")
    expect(page.locator("h1")).to_contain_text("Spending")
