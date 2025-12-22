# Week 05: Views & URLs - Deep Dive

## 🎯 Learning Objectives

By the end of this week, you will:

- Understand Function-Based Views (FBVs) vs Class-Based Views (CBVs)
- Master URL patterns with path converters and regex
- Handle HTTP methods properly (GET, POST, PUT, DELETE)
- Work with request/response objects
- Implement redirects, error handling, and HTTP responses

## 📚 Required Reading

| Resource                                                                             | Section      | Time   |
| ------------------------------------------------------------------------------------ | ------------ | ------ |
| [Writing Views](https://docs.djangoproject.com/en/5.0/topics/http/views/)            | Full page    | 30 min |
| [URL Dispatcher](https://docs.djangoproject.com/en/5.0/topics/http/urls/)            | Full page    | 30 min |
| [Class-based Views](https://docs.djangoproject.com/en/5.0/topics/class-based-views/) | Introduction | 30 min |
| [Request/Response](https://docs.djangoproject.com/en/5.0/ref/request-response/)      | Full page    | 20 min |

---

## Part 1: Function-Based Views (FBVs)

### The Anatomy of a View

```
┌─────────────────────────────────────────────────────────────────┐
│                    View Function Flow                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   HttpRequest ──► View Function ──► HttpResponse                │
│                        │                                         │
│                        ├── Read request data                     │
│                        ├── Query database                        │
│                        ├── Process business logic                │
│                        ├── Render template                       │
│                        └── Return response                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Exercise 5.1: Complete FBV Examples

```python
# tasks/views.py
from django.http import (
    HttpRequest, HttpResponse, JsonResponse,
    HttpResponseRedirect, Http404, HttpResponseBadRequest
)
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.core.paginator import Paginator

from .models import Task, Category, Status, Priority


# Basic view
def task_list(request: HttpRequest) -> HttpResponse:
    """List all tasks with filtering and pagination."""
    tasks = Task.objects.select_related('category').prefetch_related('tags')

    # Filter by status (query parameter)
    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)

    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        tasks = tasks.filter(category_id=category_id)

    # Pagination
    paginator = Paginator(tasks, 10)  # 10 tasks per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'statuses': Status.choices,
        'current_status': status,
        'current_category': category_id,
    }
    return render(request, 'tasks/task_list.html', context)


# Detail view with 404 handling
def task_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Show task details."""
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})


# Handle multiple HTTP methods
@require_http_methods(["GET", "POST"])
def task_create(request: HttpRequest) -> HttpResponse:
    """Create a new task."""
    if request.method == 'POST':
        # Process form data
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        priority = request.POST.get('priority', Priority.MEDIUM)
        category_id = request.POST.get('category')

        # Validation
        if not title:
            return render(request, 'tasks/task_form.html', {
                'error': 'Title is required',
                'categories': Category.objects.all(),
            })

        # Create task
        task = Task.objects.create(
            title=title,
            description=description,
            priority=priority,
            category_id=category_id if category_id else None,
        )

        # Redirect to detail page
        return redirect('tasks:task_detail', pk=task.pk)

    # GET request - show form
    return render(request, 'tasks/task_form.html', {
        'categories': Category.objects.all(),
        'priorities': Priority.choices,
    })


# JSON response for API-like endpoints
def task_api_list(request: HttpRequest) -> JsonResponse:
    """Return tasks as JSON."""
    tasks = Task.objects.all().values(
        'id', 'title', 'status', 'priority', 'created_at'
    )
    return JsonResponse({'tasks': list(tasks)})


# Update with method restriction
@require_POST
def task_complete(request: HttpRequest, pk: int) -> HttpResponse:
    """Mark a task as complete."""
    task = get_object_or_404(Task, pk=pk)
    task.mark_complete()

    # Check if AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'task_id': pk})

    return redirect('tasks:task_detail', pk=pk)


# Delete with confirmation
@require_http_methods(["GET", "POST"])
def task_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete a task."""
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        task.delete()
        return redirect('tasks:task_list')

    return render(request, 'tasks/task_confirm_delete.html', {'task': task})
```

---

## Part 2: Class-Based Views (CBVs)

### Why Class-Based Views?

```
┌─────────────────────────────────────────────────────────────────┐
│                    FBV vs CBV Comparison                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Function-Based Views (FBV)       Class-Based Views (CBV)        │
│  ─────────────────────────        ───────────────────────        │
│  ✓ Simple and explicit            ✓ Reusable via inheritance     │
│  ✓ Easy to understand             ✓ Built-in generic views       │
│  ✓ Good for one-off views         ✓ DRY (mixins)                 │
│  ✗ Code duplication               ✓ HTTP methods as methods      │
│  ✗ Hard to extend                 ✗ More complex/magic           │
│                                                                  │
│  USE FBV WHEN:                    USE CBV WHEN:                  │
│  - Simple, one-off logic          - Standard CRUD operations     │
│  - Custom processing              - Need to override behavior    │
│  - Easier to understand           - Reuse across views           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Exercise 5.2: Generic Class-Based Views

```python
# tasks/views.py
from django.views.generic import (
    ListView, DetailView, CreateView,
    UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.contrib import messages


class TaskListView(ListView):
    """List tasks with pagination and filtering."""
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10

    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = Task.objects.select_related('category').prefetch_related('tags')

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        return queryset

    def get_context_data(self, **kwargs):
        """Add extra context."""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['statuses'] = Status.choices
        return context


class TaskDetailView(DetailView):
    """Show task details."""
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        """Optimize query with related objects."""
        return Task.objects.select_related('category').prefetch_related('tags')


class TaskCreateView(CreateView):
    """Create a new task."""
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['title', 'description', 'priority', 'status', 'category', 'due_date', 'tags']

    def get_success_url(self):
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)


class TaskUpdateView(UpdateView):
    """Update an existing task."""
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['title', 'description', 'priority', 'status', 'category', 'due_date', 'tags']

    def get_success_url(self):
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)


class TaskDeleteView(DeleteView):
    """Delete a task."""
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')

    def form_valid(self, form):
        messages.success(self.request, 'Task deleted successfully!')
        return super().form_valid(form)


class DashboardView(TemplateView):
    """Dashboard with statistics."""
    template_name = 'tasks/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_tasks'] = Task.objects.count()
        context['completed_tasks'] = Task.objects.filter(status=Status.COMPLETED).count()
        context['pending_tasks'] = Task.objects.filter(status=Status.PENDING).count()
        context['categories'] = Category.objects.annotate(
            task_count=models.Count('tasks')
        )
        return context
```

---

## Part 3: Advanced URL Patterns

### Exercise 5.3: URL Configuration

```python
# tasks/urls.py
from django.urls import path, re_path, include
from . import views

app_name = 'tasks'

urlpatterns = [
    # Function-based views
    path('', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('<int:pk>/', views.task_detail, name='task_detail'),
    path('<int:pk>/complete/', views.task_complete, name='task_complete'),
    path('<int:pk>/delete/', views.task_delete, name='task_delete'),

    # Class-based views (alternative)
    # path('', views.TaskListView.as_view(), name='task_list'),
    # path('<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    # path('create/', views.TaskCreateView.as_view(), name='task_create'),
    # path('<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    # path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),

    # Slug-based URLs
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),

    # Multiple parameters
    path('archive/<int:year>/<int:month>/', views.archive, name='archive'),

    # API endpoints
    path('api/tasks/', views.task_api_list, name='api_task_list'),
    path('api/tasks/<int:pk>/', views.task_api_detail, name='api_task_detail'),
]

# URL namespacing and includes in config/urls.py:
# path('tasks/', include('tasks.urls', namespace='tasks')),
```

### Path Converters Reference

| Converter | Matches                            | Example        |
| --------- | ---------------------------------- | -------------- |
| `str`     | Any non-empty string except `/`    | `hello-world`  |
| `int`     | Zero or positive integer           | `42`           |
| `slug`    | ASCII letters, numbers, `-`, `_`   | `my-slug_123`  |
| `uuid`    | UUID format                        | `075194d3-...` |
| `path`    | Any non-empty string including `/` | `path/to/file` |

### Custom Path Converter

```python
# tasks/converters.py
class FourDigitYearConverter:
    regex = '[0-9]{4}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%04d' % value

# Register in urls.py
from django.urls import register_converter
from . import converters

register_converter(converters.FourDigitYearConverter, 'yyyy')

urlpatterns = [
    path('archive/<yyyy:year>/', views.archive, name='archive'),
]
```

---

## Part 4: Request and Response Objects

### Exercise 5.4: Working with HttpRequest

```python
def request_inspector(request: HttpRequest) -> HttpResponse:
    """Demonstrate HttpRequest attributes."""
    info = {
        # Request metadata
        'method': request.method,
        'path': request.path,
        'full_path': request.get_full_path(),
        'absolute_uri': request.build_absolute_uri(),

        # GET parameters (?key=value)
        'GET_params': dict(request.GET),

        # POST data (form submissions)
        'POST_data': dict(request.POST) if request.method == 'POST' else {},

        # Headers
        'content_type': request.content_type,
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'host': request.get_host(),

        # User info
        'user': str(request.user),
        'is_authenticated': request.user.is_authenticated,

        # AJAX detection
        'is_ajax': request.headers.get('X-Requested-With') == 'XMLHttpRequest',
    }
    return JsonResponse(info)
```

### Response Types

```python
from django.http import (
    HttpResponse,
    JsonResponse,
    FileResponse,
    StreamingHttpResponse,
    HttpResponseRedirect,
    HttpResponsePermanentRedirect,
    HttpResponseNotFound,
    HttpResponseForbidden,
    HttpResponseBadRequest,
)

# Plain text
def plain_text(request):
    return HttpResponse("Hello", content_type="text/plain")

# JSON
def json_response(request):
    return JsonResponse({'message': 'Hello'})

# File download
def download_file(request):
    file_path = '/path/to/file.pdf'
    return FileResponse(open(file_path, 'rb'), as_attachment=True)

# Redirect
def redirect_example(request):
    return redirect('tasks:task_list')  # Using URL name
    # return redirect('/tasks/')  # Using path
    # return HttpResponseRedirect(reverse('tasks:task_list'))

# Error responses
def not_found(request):
    return HttpResponseNotFound('<h1>Page not found</h1>')

def forbidden(request):
    return HttpResponseForbidden('<h1>Access denied</h1>')

# Custom status code
def custom_status(request):
    return HttpResponse('Created', status=201)
```

---

## 📝 Weekly Project: Complete TaskMaster Views

Implement all CRUD views for TaskMaster with proper URL patterns:

```python
# tasks/urls.py - Complete URL configuration
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Task CRUD
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),

    # Task actions
    path('tasks/<int:pk>/complete/', views.task_complete, name='task_complete'),
    path('tasks/<int:pk>/reopen/', views.task_reopen, name='task_reopen'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),

    # API
    path('api/tasks/', views.api_task_list, name='api_task_list'),
    path('api/tasks/<int:pk>/', views.api_task_detail, name='api_task_detail'),
]
```

---

## 📋 Submission Checklist

- [ ] Implemented FBV for all CRUD operations
- [ ] Implemented equivalent CBV alternatives
- [ ] URL patterns with namespacing
- [ ] Proper HTTP method handling
- [ ] Pagination working
- [ ] Filtering by status and category
- [ ] JSON API endpoints
- [ ] Error handling (404s)

---

**Next**: [Week 06: Templates →](../week-06-templates/README.md)
