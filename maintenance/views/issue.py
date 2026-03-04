from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from maintenance.forms import IssueForm
from maintenance.models import Issue


@login_required
def issue_list(request):
    qs = Issue.objects.select_related("asset", "location", "project")

    # Filters
    status = request.GET.get("status", "active")
    severity = request.GET.get("severity", "")
    search = request.GET.get("q", "").strip()

    if status == "active":
        qs = qs.exclude(status="resolved")
    elif status:
        qs = qs.filter(status=status)

    if severity:
        qs = qs.filter(severity=severity)
    if search:
        qs = qs.filter(summary__icontains=search)

    context = {
        "issues": qs,
        "statuses": Issue.STATUS_CHOICES,
        "severities": Issue.SEVERITY_CHOICES,
        "filters": {
            "status": status,
            "severity": severity,
            "q": search,
        },
    }
    return render(request, "issues/list.html", context)


@login_required
def issue_detail(request, pk):
    issue = get_object_or_404(
        Issue.objects.select_related("asset", "location", "project"), pk=pk
    )

    return render(request, "issues/detail.html", {"issue": issue})


@login_required
def issue_create(request):
    if request.method == "POST":
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save()
            return redirect("issue_detail", pk=issue.pk)
    else:
        form = IssueForm()

    return render(request, "issues/form.html", {"form": form, "editing": False})


@login_required
def issue_edit(request, pk):
    issue = get_object_or_404(Issue, pk=pk)

    if request.method == "POST":
        form = IssueForm(request.POST, instance=issue)
        if form.is_valid():
            form.save()
            return redirect("issue_detail", pk=issue.pk)
    else:
        form = IssueForm(instance=issue)

    return render(request, "issues/form.html", {
        "form": form,
        "issue": issue,
        "editing": True,
    })
