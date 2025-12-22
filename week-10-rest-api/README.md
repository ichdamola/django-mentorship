# Week 10: Django REST Framework

## 🎯 Learning Objectives

- Build RESTful APIs with Django REST Framework (DRF)
- Create serializers for your models
- Implement viewsets and routers
- Handle authentication and permissions
- Document your API

## 📚 Required Reading

| Resource                                                                    | Section   | Time   |
| --------------------------------------------------------------------------- | --------- | ------ |
| [DRF Tutorial](https://www.django-rest-framework.org/tutorial/quickstart/)  | All parts | 60 min |
| [Serializers](https://www.django-rest-framework.org/api-guide/serializers/) | Full page | 30 min |
| [ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/)       | Full page | 20 min |

---

## Setup

```bash
uv add djangorestframework
```

```python
# config/settings.py
INSTALLED_APPS = [
    ...
    'rest_framework',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

---

## Key Concepts

### Serializers

```python
# tasks/serializers.py
from rest_framework import serializers
from .models import Task, Category, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    task_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'task_count']


class TaskSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',
        write_only=True,
        many=True,
        required=False
    )
    is_overdue = serializers.BooleanField(read_only=True)
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status',
            'category', 'category_id', 'tags', 'tag_ids',
            'due_date', 'is_overdue', 'owner',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
```

### ViewSets

```python
# tasks/views_api.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count

from .models import Task, Category, Tag
from .serializers import TaskSerializer, CategorySerializer, TagSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            owner=self.request.user
        ).select_related('category').prefetch_related('tags')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.mark_complete()
        return Response({'status': 'completed'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        return Response({
            'total': queryset.count(),
            'completed': queryset.filter(status='completed').count(),
            'pending': queryset.filter(status='pending').count(),
        })


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(task_count=Count('tasks'))
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
```

### URL Routing

```python
# tasks/urls_api.py
from rest_framework.routers import DefaultRouter
from . import views_api

router = DefaultRouter()
router.register('tasks', views_api.TaskViewSet, basename='task')
router.register('categories', views_api.CategoryViewSet, basename='category')
router.register('tags', views_api.TagViewSet, basename='tag')

urlpatterns = router.urls

# config/urls.py
urlpatterns = [
    ...
    path('api/v1/', include('tasks.urls_api')),
]
```

### API Endpoints

| Endpoint                       | Method    | Description    |
| ------------------------------ | --------- | -------------- |
| `/api/v1/tasks/`               | GET       | List all tasks |
| `/api/v1/tasks/`               | POST      | Create task    |
| `/api/v1/tasks/{id}/`          | GET       | Get task       |
| `/api/v1/tasks/{id}/`          | PUT/PATCH | Update task    |
| `/api/v1/tasks/{id}/`          | DELETE    | Delete task    |
| `/api/v1/tasks/{id}/complete/` | POST      | Mark complete  |
| `/api/v1/tasks/stats/`         | GET       | Get statistics |

---

## 📋 Submission Checklist

- [ ] DRF installed and configured
- [ ] Serializers for all models
- [ ] ViewSets with CRUD operations
- [ ] Custom actions (complete, stats)
- [ ] API authentication working
- [ ] API documentation viewable at `/api/v1/`

---

**Next**: [Week 11: Testing →](../week-11-testing/README.md)
