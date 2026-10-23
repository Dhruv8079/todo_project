from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import TaskForm
from .models import Task


class TaskModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='owner', email='owner@example.com', password='pass12345'
        )
        self.task = Task.objects.create(
            user=self.user,
            title='Write report',
            description='Quarterly report',
            category='work',
            priority='high',
            due_date=timezone.now() + timedelta(days=1),
        )

    def test_str_returns_title(self):
        self.assertEqual(str(self.task), 'Write report')

    def test_defaults(self):
        task = Task.objects.create(user=self.user, title='Fresh task')
        self.assertFalse(task.is_completed)
        self.assertEqual(task.priority, 'medium')
        self.assertEqual(task.category, 'other')

    def test_is_overdue_false_for_future_due_date(self):
        self.assertFalse(self.task.is_overdue)

    def test_is_overdue_true_when_past_and_pending(self):
        past = Task.objects.create(
            user=self.user, title='Late', due_date=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(past.is_overdue)

    def test_is_overdue_false_when_completed(self):
        past = Task.objects.create(
            user=self.user,
            title='Late but done',
            due_date=timezone.now() - timedelta(days=1),
            is_completed=True,
        )
        self.assertFalse(past.is_overdue)


class TaskFormTests(TestCase):
    def test_valid_form(self):
        form = TaskForm(data={
            'title': 'Valid task',
            'description': 'desc',
            'category': 'study',
            'priority': 'low',
            'due_date': (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_title_required(self):
        form = TaskForm(data={'title': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_title_max_length(self):
        form = TaskForm(data={'title': 'a' * 201})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_invalid_priority_rejected(self):
        form = TaskForm(data={'title': 'Bad priority', 'priority': 'urgent'})
        self.assertFalse(form.is_valid())
        self.assertIn('priority', form.errors)


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice', email='alice@example.com', password='pass12345'
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_login_with_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'alice', 'password': 'pass12345'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('tasks:dashboard'))

    def test_login_with_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'alice', 'password': 'wrong'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct')

    def test_register_creates_and_logs_in_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'bobby',
            'password1': 'StrongPass!234',
            'password2': 'StrongPass!234',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='bobby').exists())
        # logged in
        self.assertEqual(int(self.client.session['_auth_user_id']),
                         User.objects.get(username='bobby').pk)

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post(reverse('register'), {
            'username': 'carl',
            'password1': 'StrongPass!234',
            'password2': 'Different!234',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='carl').exists())

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_renders(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)


class TaskAccessTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pass12345')
        self.intruder = User.objects.create_user(username='intruder', password='pass12345')
        self.task = Task.objects.create(user=self.owner, title='Private task')
        self.client.force_login(self.intruder)

    def test_cannot_view_other_users_task(self):
        response = self.client.get(reverse('tasks:task-detail', args=[self.task.pk]))
        self.assertEqual(response.status_code, 404)

    def test_cannot_update_other_users_task(self):
        response = self.client.post(
            reverse('tasks:task-update', args=[self.task.pk]),
            {'title': 'Hacked', 'category': 'work', 'priority': 'low'},
        )
        self.assertEqual(response.status_code, 404)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Private task')

    def test_cannot_delete_other_users_task(self):
        response = self.client.post(reverse('tasks:task-delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

    def test_cannot_complete_other_users_task(self):
        response = self.client.post(reverse('tasks:task-complete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 404)
        self.task.refresh_from_db()
        self.assertFalse(self.task.is_completed)

    def test_dashboard_only_lists_own_tasks(self):
        Task.objects.create(user=self.intruder, title='My own task')
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertContains(response, 'My own task')
        self.assertNotContains(response, 'Private task')


class TaskCrudTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='worker', password='pass12345')
        self.client.force_login(self.user)
        self.task = Task.objects.create(
            user=self.user, title='Original title', category='work', priority='medium'
        )

    def test_create_task_assigns_owner(self):
        response = self.client.post(reverse('tasks:task-create'), {
            'title': 'Created via view',
            'description': 'hello',
            'category': 'personal',
            'priority': 'high',
        })
        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(title='Created via view')
        self.assertEqual(task.user, self.user)

    def test_create_task_invalid_shows_form(self):
        response = self.client.post(reverse('tasks:task-create'), {'title': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

    def test_update_task(self):
        response = self.client.post(reverse('tasks:task-update', args=[self.task.pk]), {
            'title': 'Updated title',
            'category': 'study',
            'priority': 'low',
        })
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated title')
        self.assertEqual(self.task.priority, 'low')

    def test_delete_task(self):
        response = self.client.post(reverse('tasks:task-delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())

    def test_delete_confirmation_page(self):
        response = self.client.get(reverse('tasks:task-delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Original title')

    def test_complete_then_reopen(self):
        self.client.post(reverse('tasks:task-complete', args=[self.task.pk]))
        self.task.refresh_from_db()
        self.assertTrue(self.task.is_completed)

        self.client.post(reverse('tasks:task-complete', args=[self.task.pk]))
        self.task.refresh_from_db()
        self.assertFalse(self.task.is_completed)

    def test_completed_view_lists_only_completed(self):
        Task.objects.create(user=self.user, title='Done task', is_completed=True)
        response = self.client.get(reverse('tasks:completed-tasks'))
        self.assertContains(response, 'Done task')
        self.assertNotContains(response, 'Original title')

    def test_profile_page(self):
        response = self.client.get(reverse('tasks:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'worker')

    def test_pagination_present_with_many_tasks(self):
        for i in range(15):
            Task.objects.create(user=self.user, title=f'Bulk task {i}')
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['tasks']), 9)


class TaskSearchFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='searcher', password='pass12345')
        self.client.force_login(self.user)
        Task.objects.create(user=self.user, title='Buy milk', description='groceries', category='personal', priority='low')
        Task.objects.create(user=self.user, title='Finish report', description='office work', category='work', priority='high')

    def test_search_by_title(self):
        response = self.client.get(reverse('tasks:task-search'), {'q': 'milk'})
        self.assertContains(response, 'Buy milk')
        self.assertNotContains(response, 'Finish report')

    def test_search_by_description(self):
        response = self.client.get(reverse('tasks:task-search'), {'q': 'office'})
        self.assertContains(response, 'Finish report')
        self.assertNotContains(response, 'Buy milk')

    def test_filter_by_priority(self):
        response = self.client.get(reverse('tasks:task-by-priority', args=['high']))
        self.assertContains(response, 'Finish report')
        self.assertNotContains(response, 'Buy milk')

    def test_filter_by_category(self):
        response = self.client.get(reverse('tasks:task-by-category', args=['personal']))
        self.assertContains(response, 'Buy milk')
        self.assertNotContains(response, 'Finish report')


class DashboardStatsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='stats', password='pass12345')
        self.client.force_login(self.user)

    def test_statistics_are_correct(self):
        Task.objects.create(user=self.user, title='Done 1', is_completed=True)
        Task.objects.create(user=self.user, title='Done 2', is_completed=True)
        Task.objects.create(user=self.user, title='Pending')
        Task.objects.create(
            user=self.user, title='Overdue',
            due_date=timezone.now() - timedelta(days=1),
        )

        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.context['total_tasks'], 4)
        self.assertEqual(response.context['completed_tasks'], 2)
        self.assertEqual(response.context['pending_tasks'], 2)
        self.assertEqual(response.context['overdue_tasks'], 1)
        self.assertEqual(response.context['completion_percentage'], 50)

    def test_empty_dashboard_is_zero_not_error(self):
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['completion_percentage'], 0)


class AdminTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='pass12345'
        )
        self.client.force_login(self.admin)

    def test_task_admin_changelist(self):
        Task.objects.create(user=self.admin, title='Admin task')
        response = self.client.get('/admin/tasks/task/')
        self.assertEqual(response.status_code, 200)

    def test_user_admin_changelist(self):
        response = self.client.get('/admin/auth/user/')
        self.assertEqual(response.status_code, 200)
