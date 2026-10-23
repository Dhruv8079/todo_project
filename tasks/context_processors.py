from tasks.models import Task


def task_stats(request):
    """Expose sidebar counters to every template."""
    if not request.user.is_authenticated:
        return {'sidebar_total': 0, 'sidebar_completed': 0, 'sidebar_pending': 0}
    qs = Task.objects.filter(user=request.user)
    total = qs.count()
    completed = qs.filter(is_completed=True).count()
    return {
        'sidebar_total': total,
        'sidebar_completed': completed,
        'sidebar_pending': total - completed,
    }
