from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from maintenance.forms import CategoryForm
from maintenance.models import Category


@login_required
def category_list(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.annotate(
        asset_count=Count("asset", distinct=True),
        schedule_count=Count("schedule", distinct=True),
        project_count=Count("project", distinct=True),
    )
    return render(request, "categories/list.html", {"categories": categories})


@login_required
def category_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("category_list")
    else:
        form = CategoryForm()
    return render(request, "categories/form.html", {"form": form, "editing": False})


@login_required
def category_edit(request: HttpRequest, pk: int) -> HttpResponse:
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("category_list")
    else:
        form = CategoryForm(instance=category)
    return render(request, "categories/form.html", {"form": form, "category": category, "editing": True})


@login_required
@require_POST
def category_delete(request: HttpRequest, pk: int) -> HttpResponse:
    category = get_object_or_404(Category, pk=pk)
    category.delete()  # SET_NULL on all FKs — safe to delete
    return redirect("category_list")
