"""Seed the database with a demo account and sample tasks.

Usage:
    python manage.py seed_demo
    python manage.py seed_demo --username demo --password demo12345
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from tasks.models import Task


SAMPLE_TASKS = [
    {
        'title': 'Finish quarterly report',
        'description': 'Compile Q3 numbers and send to the finance team.',
        'category': 'work',
        'priority': 'high',
        'due_in_days': 2,
        'is_completed': False,
    },
    {
        'title': 'Prepare slides for client meeting',
        'description': 'Slides covering roadmap, timeline and budget.',
        'category': 'work',
        'priority': 'high',
        'due_in_days': 1,
        'is_completed': False,
    },
    {
        'title': 'Review pull requests',
        'description': 'Clear the review queue before the weekend.',
        'category': 'work',
        'priority': 'medium',
        'due_in_days': 0,
        'is_completed': False,
    },
    {
        'title': 'Read two chapters of Django docs',
        'description': 'Focus on class-based views and forms.',
        'category': 'study',
        'priority': 'medium',
        'due_in_days': 5,
        'is_completed': False,
    },
    {
        'title': 'Buy groceries',
        'description': 'Milk, eggs, rice, vegetables and coffee.',
        'category': 'personal',
        'priority': 'low',
        'due_in_days': 1,
        'is_completed': False,
    },
    {
        'title': 'Book dentist appointment',
        'description': 'Routine check-up, preferably next week.',
        'category': 'personal',
        'priority': 'medium',
        'due_in_days': -1,
        'is_completed': False,
    },
    {
        'title': 'Pay electricity bill',
        'description': 'Overdue by a few days - pay immediately.',
        'category': 'personal',
        'priority': 'high',
        'due_in_days': -3,
        'is_completed': False,
    },
    {
        'title': 'Renew gym membership',
        'description': 'Annual plan renewal.',
        'category': 'personal',
        'priority': 'low',
        'due_in_days': 10,
        'is_completed': True,
    },
    {
        'title': 'Set up project repository',
        'description': 'Initialise git, add README and .gitignore.',
        'category': 'work',
        'priority': 'medium',
        'due_in_days': -5,
        'is_completed': True,
    },
    {
        'title': 'Plan weekend trip',
        'description': 'Decide destination and book a hotel.',
        'category': 'other',
        'priority': 'low',
        'due_in_days': 7,
        'is_completed': False,
    },
]


class Command(BaseCommand):
    help = 'Create a demo user with sample tasks for testing.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='demo')
        parser.add_argument('--password', default='demo12345')
        parser.add_argument('--email', default='demo@example.com')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']

        user, created = User.objects.get_or_create(
            username=username, defaults={'email': email}
        )
        if created:
            user.set_password(password)
            user.email = email
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'Created user "{username}" with password "{password}".'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'User "{username}" already exists - reusing it.'
            ))

        if user.task_set.exists():
            self.stdout.write(self.style.WARNING(
                'Demo user already has tasks; existing tasks were left untouched.'
            ))
            return

        now = timezone.now()
        tasks = []
        for item in SAMPLE_TASKS:
            tasks.append(Task(
                user=user,
                title=item['title'],
                description=item['description'],
                category=item['category'],
                priority=item['priority'],
                due_date=now + timedelta(days=item['due_in_days']),
                is_completed=item['is_completed'],
            ))
        Task.objects.bulk_create(tasks)

        self.stdout.write(self.style.SUCCESS(
            f'Created {len(tasks)} sample tasks for "{username}".'
        ))
        self.stdout.write('Log in at http://127.0.0.1:8000/accounts/login/')
