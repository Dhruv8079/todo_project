"""URL configuration for todo_project project."""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from tasks import views as task_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', task_views.RegisterView.as_view(), name='register'),

    # Tasks
    path('', include('tasks.urls')),
]
