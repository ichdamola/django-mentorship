# Week 08: Django Admin Customization

## 🎯 Learning Objectives

- Configure Django admin for your models
- Customize list views, filters, and search
- Create custom admin actions
- Use inlines for related models
- Customize admin forms and templates

## 📚 Required Reading

| Resource                                                                          | Section   | Time   |
| --------------------------------------------------------------------------------- | --------- | ------ |
| [Django Admin Site](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/)     | Full page | 60 min |
| [Admin Actions](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/actions/) | Full page | 20 min |

---

## Key Concepts

### Basic Admin Registration

```python
# tasks/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Task, Category, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'colored_badge', 'task_count', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']

    def colored_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; '
            'border-radius: 3px; color: white;">{}</span>',
            obj.color, obj.name
        )
    colored_badge.short_description = 'Badge'

    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Tasks'


class TagInline(admin.TabularInline):
    model = Task.tags.through
    extra = 1


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'category', 'due_date', 'is_overdue']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['status', 'priority']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = [
        (None, {
            'fields': ['title', 'description']
        }),
        ('Status', {
            'fields': ['status', 'priority', 'category']
        }),
        ('Dates', {
            'fields': ['due_date', 'created_at', 'updated_at', 'completed_at'],
            'classes': ['collapse']
        }),
    ]
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    filter_horizontal = ['tags']

    # Custom actions
    actions = ['mark_completed', 'mark_pending']

    @admin.action(description='Mark selected tasks as completed')
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} tasks marked as completed.')

    @admin.action(description='Mark selected tasks as pending')
    def mark_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} tasks marked as pending.')

    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue?'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'task_count']
    search_fields = ['name']

    def task_count(self, obj):
        return obj.tasks.count()
```

### Create Superuser

```bash
uv run python manage.py createsuperuser
```

---

## 📋 Submission Checklist

- [ ] All models registered in admin
- [ ] Custom list displays
- [ ] Filters and search configured
- [ ] Custom admin actions
- [ ] Inlines for related models

---

**Next**: [Week 09: Authentication →](../week-09-authentication/README.md)
