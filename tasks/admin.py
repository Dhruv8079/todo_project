from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'category', 'is_completed', 'due_date', 'created_at')
    list_filter = ('priority', 'category', 'is_completed', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'description')
        }),
        ('Classification', {
            'fields': ('category', 'priority'),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('due_date',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_completed',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')


# Extend the built-in User admin with task-related info
class UserTaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ('title', 'priority', 'category', 'is_completed', 'due_date')
    show_change_link = True


admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserTaskInline]
    list_display = ('username', 'email', 'is_staff', 'date_joined', 'task_count')
    search_fields = ('username', 'email')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('task_set')

    @admin.display(description='Tasks')
    def task_count(self, obj):
        return obj.task_set.count()
