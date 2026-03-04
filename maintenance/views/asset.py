from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from maintenance.forms import AssetForm
from maintenance.models import Asset, Location


@login_required
def asset_list(request):
    qs = Asset.objects.select_related("location")

    # Filters
    category = request.GET.get("category", "")
    location_id = request.GET.get("location", "")
    search = request.GET.get("q", "").strip()

    if category:
        qs = qs.filter(category=category)
    if location_id:
        qs = qs.filter(location_id=location_id)
    if search:
        qs = qs.filter(name__icontains=search)

    locations = Location.objects.all()

    context = {
        "assets": qs,
        "categories": Asset.CATEGORY_CHOICES,
        "locations": locations,
        "filters": {
            "category": category,
            "location": location_id,
            "q": search,
        },
    }
    return render(request, "assets/list.html", context)


@login_required
def asset_detail(request, pk):
    asset = get_object_or_404(Asset.objects.select_related("location"), pk=pk)

    schedules = asset.schedules.filter(active=True)
    projects = asset.projects.all()
    issues = asset.issues.all()
    work_logs = asset.work_logs.order_by("-completed_at")[:10]

    return render(request, "assets/detail.html", {
        "asset": asset,
        "schedules": schedules,
        "projects": projects,
        "issues": issues,
        "work_logs": work_logs,
    })


@login_required
def asset_create(request):
    if request.method == "POST":
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save()
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = AssetForm()

    return render(request, "assets/form.html", {"form": form, "editing": False})


@login_required
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)

    if request.method == "POST":
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            return redirect("asset_detail", pk=asset.pk)
    else:
        form = AssetForm(instance=asset)

    return render(request, "assets/form.html", {
        "form": form,
        "asset": asset,
        "editing": True,
    })
