from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from maintenance.forms import ProjectForm
from maintenance.models import Project


def project_list(request):
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

    today = timezone.now().date()
    projects = []
    for p in qs:
        if p.status in ("done", "cancelled"):
            p.effective_status_display = p.status
        elif p.status == "someday":
            p.effective_status_display = "someday"
        elif p.target_date and p.target_date < today:
            p.effective_status_display = "overdue"
        elif p.target_date and (p.target_date - today).days <= 14:
            p.effective_status_display = "due_soon"
        else:
            p.effective_status_display = p.status
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


def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("asset", "location"), pk=pk
    )

    today = timezone.now().date()
    if project.status in ("done", "cancelled"):
        project.effective_status_display = project.status
    elif project.status == "someday":
        project.effective_status_display = "someday"
    elif project.target_date and project.target_date < today:
        project.effective_status_display = "overdue"
    elif project.target_date and (project.target_date - today).days <= 14:
        project.effective_status_display = "due_soon"
    else:
        project.effective_status_display = project.status

    work_logs = project.work_logs.order_by("-completed_at")[:20]
    issues = project.issues.all()

    return render(request, "projects/detail.html", {
        "project": project,
        "work_logs": work_logs,
        "issues": issues,
    })


def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            return redirect("project_detail", pk=project.pk)
    else:
        form = ProjectForm()

    return render(request, "projects/form.html", {"form": form, "editing": False})


def project_edit(request, pk):
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
