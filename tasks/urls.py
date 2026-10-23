from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Dashboard (default task list)
    path('', views.TaskListView.as_view(), name='dashboard'),

    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # Completed tasks
    path('completed/', views.CompletedTasksView.as_view(), name='completed-tasks'),

    # Search tasks
    path('search/', views.TaskSearchView.as_view(), name='task-search'),

    # Filter by priority
    path('priority/<str:priority>/', views.TaskByPriorityView.as_view(), name='task-by-priority'),

    # Filter by category
    path('category/<str:category>/', views.TaskByCategoryView.as_view(), name='task-by-category'),

    # Create task
    path('task/create/', views.TaskCreateView.as_view(), name='task-create'),

    # Task detail
    path('task/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),

    # Update task
    path('task/<int:pk>/update/', views.TaskUpdateView.as_view(), name='task-update'),

    # Delete task
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task-delete'),

    # Complete/Reopen task
    path('task/<int:pk>/complete/', views.TaskCompleteView.as_view(), name='task-complete'),
]
