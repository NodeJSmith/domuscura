import pytest
from django.test import Client
from django.urls import reverse

from maintenance.models import Asset


@pytest.fixture
def client():
    return Client()


class TestAssetList:
    def test_list_loads(self, client, db):
        resp = client.get(reverse("asset_list"))
        assert resp.status_code == 200

    def test_list_shows_assets(self, client, asset):
        resp = client.get(reverse("asset_list"))
        assert "Central AC" in str(resp.content)

    def test_list_filter_by_category(self, client, asset):
        resp = client.get(reverse("asset_list"), {"category": "HVAC"})
        assert len(resp.context["assets"]) == 1

        resp = client.get(reverse("asset_list"), {"category": "Plumbing"})
        assert len(resp.context["assets"]) == 0

    def test_list_filter_by_location(self, client, asset, location):
        resp = client.get(reverse("asset_list"), {"location": location.pk})
        assert len(resp.context["assets"]) == 1

    def test_list_filter_by_search(self, client, asset):
        resp = client.get(reverse("asset_list"), {"q": "Central"})
        assert len(resp.context["assets"]) == 1

        resp = client.get(reverse("asset_list"), {"q": "nonexistent"})
        assert len(resp.context["assets"]) == 0


class TestAssetDetail:
    def test_detail_loads(self, client, asset):
        resp = client.get(reverse("asset_detail", args=[asset.pk]))
        assert resp.status_code == 200
        assert resp.context["asset"].name == "Central AC"

    def test_detail_shows_related(self, client, asset, schedule):
        resp = client.get(reverse("asset_detail", args=[asset.pk]))
        assert len(resp.context["schedules"]) == 1

    def test_detail_404(self, client, db):
        resp = client.get(reverse("asset_detail", args=[99999]))
        assert resp.status_code == 404


class TestAssetCreate:
    def test_create_get(self, client, db):
        resp = client.get(reverse("asset_create"))
        assert resp.status_code == 200
        assert resp.context["editing"] is False

    def test_create_post_valid(self, client, db):
        resp = client.post(reverse("asset_create"), {
            "name": "New Asset",
            "category": "Plumbing",
        })
        assert resp.status_code == 302
        assert Asset.objects.filter(name="New Asset").exists()

    def test_create_post_invalid(self, client, db):
        resp = client.post(reverse("asset_create"), {"name": ""})
        assert resp.status_code == 200


class TestAssetEdit:
    def test_edit_get(self, client, asset):
        resp = client.get(reverse("asset_edit", args=[asset.pk]))
        assert resp.status_code == 200
        assert resp.context["editing"] is True

    def test_edit_post_valid(self, client, asset):
        resp = client.post(reverse("asset_edit", args=[asset.pk]), {
            "name": "Updated AC",
            "category": "HVAC",
        })
        assert resp.status_code == 302
        asset.refresh_from_db()
        assert asset.name == "Updated AC"

    def test_edit_404(self, client, db):
        resp = client.get(reverse("asset_edit", args=[99999]))
        assert resp.status_code == 404
