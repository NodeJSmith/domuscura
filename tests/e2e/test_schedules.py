import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.e2e


def test_schedule_list_shows_schedules(page, base_url, seeded_db):
    page.goto(f"{base_url}/schedules/")
    expect(page.locator("text=Replace HVAC Filter")).to_be_visible()


def test_schedule_create_flow(page, base_url, seeded_db):
    page.goto(f"{base_url}/schedules/new/")
    page.locator("input[name='name']").fill("Test New Schedule")
    page.locator("input[name='frequency_days']").fill("30")
    page.locator("select[name='priority']").select_option("normal")
    page.get_by_role("button", name="Save").click()
    # Should redirect to detail page
    expect(page.locator("text=Test New Schedule")).to_be_visible()


def test_schedule_detail_loads(page, base_url, seeded_db):
    pk = seeded_db["schedule"].pk
    page.goto(f"{base_url}/schedules/{pk}/")
    expect(page.locator("text=Replace HVAC Filter")).to_be_visible()


def test_schedule_edit_flow(page, base_url, seeded_db):
    pk = seeded_db["schedule"].pk
    page.goto(f"{base_url}/schedules/{pk}/edit/")
    name_input = page.locator("input[name='name']")
    name_input.fill("Updated Filter Schedule")
    page.get_by_role("button", name="Save").click()
    expect(page.locator("text=Updated Filter Schedule")).to_be_visible()
