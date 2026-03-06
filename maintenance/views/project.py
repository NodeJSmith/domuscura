from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from maintenance.forms import ProjectForm
from maintenance.models import Project


@login_required
def project_list(request: HttpRequest) -> HttpResponse:
    qs = Project.objects.select_related("asset", "location")

    # Filters
    status = request.GET.get("status", "")
    priority = request.GET.get("priority", "")
    search = request.GET.get("q", "").strip()

    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)
    if search:
        qs = qs.filter(name__icontains=search)

    projects = []
    for p in qs:
        p.effective_status_display = p.effective_status
        projects.append(p)

    context = {
        "projects": projects,
        "statuses": Project.STATUS_CHOICES,
        "priorities": Project.PRIORITY_CHOICES,
        "filters": {
            "status": status,
            "priority": priority,
            "q": search,
        },
    }
    return render(request, "projects/list.html", context)


@login_required
def project_detail(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(
        Project.objects.select_related("asset", "location"), pk=pk
    )

    project.effective_status_display = project.effective_status

    work_logs = project.work_logs.order_by("-completed_at")[:20]
    issues = project.issues.all()

    return render(request, "projects/detail.html", {
        "project": project,
        "work_logs": work_logs,
        "issues": issues,
    })


@login_required
def project_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            return redirect("project_detail", pk=project.pk)
    else:
        form = ProjectForm()

    return render(request, "projects/form.html", {"form": form, "editing": False})


@login_required
def project_edit(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, "projects/form.html", {
        "form": form,
        "project": project,
        "editing": True,
    })
