from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q

from .models import Task
from .forms import TaskForm


class BootstrapUserCreationForm(UserCreationForm):
    """UserCreationForm with Bootstrap styling on every widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = 'form-check-input' if field.widget.input_type == 'checkbox' else 'form-control'
            field.widget.attrs.setdefault('class', css)
            field.widget.attrs.setdefault('placeholder', field.label)


class TaskStatsMixin:
    """Adds dashboard statistics to the template context for any task list view."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_tasks = Task.objects.filter(user=self.request.user)
        total = user_tasks.count()
        completed = user_tasks.filter(is_completed=True).count()
        context.update({
            'total_tasks': total,
            'completed_tasks': completed,
            'pending_tasks': total - completed,
            'overdue_tasks': user_tasks.filter(
                due_date__lt=timezone.now(), is_completed=False
            ).count(),
            'completion_percentage': round((completed / total) * 100) if total else 0,
        })
        return context


class TaskListView(TaskStatsMixin, LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/dashboard.html'
    context_object_name = 'tasks'
    paginate_by = 9

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def test_func(self):
        return self.get_object().user == self.request.user


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Task created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tasks:dashboard')


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def test_func(self):
        return self.get_object().user == self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tasks:dashboard')


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    context_object_name = 'task'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def test_func(self):
        return self.get_object().user == self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Task deleted successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tasks:dashboard')


class TaskCompleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs['pk'], user=request.user)
        task.is_completed = not task.is_completed
        task.save()
        action = 'completed' if task.is_completed else 'reopened'
        messages.success(request, f'Task marked as {action}.')
        return redirect('tasks:dashboard')


class CompletedTasksView(TaskStatsMixin, LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/completed_tasks.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, is_completed=True)


class TaskSearchView(TaskStatsMixin, LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/dashboard.html'
    context_object_name = 'tasks'
    paginate_by = 9

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        qs = Task.objects.filter(user=self.request.user)
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class TaskByPriorityView(TaskStatsMixin, LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/dashboard.html'
    context_object_name = 'tasks'
    paginate_by = 9

    def get_queryset(self):
        return Task.objects.filter(
            user=self.request.user, priority=self.kwargs.get('priority')
        )


class TaskByCategoryView(TaskStatsMixin, LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/dashboard.html'
    context_object_name = 'tasks'
    paginate_by = 9

    def get_queryset(self):
        return Task.objects.filter(
            user=self.request.user, category=self.kwargs.get('category')
        )


class RegisterView(CreateView):
    form_class = BootstrapUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('tasks:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('tasks:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Account created successfully. Welcome!')
        return redirect(self.success_url)


class ProfileView(LoginRequiredMixin, ListView):
    template_name = 'tasks/profile.html'
    context_object_name = 'tasks'
    paginate_by = 5

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_tasks = Task.objects.filter(user=self.request.user)
        total = user_tasks.count()
        completed = user_tasks.filter(is_completed=True).count()
        context.update({
            'total_tasks': total,
            'completed_tasks': completed,
            'pending_tasks': total - completed,
            'completion_percentage': round((completed / total) * 100) if total else 0,
        })
        return context
