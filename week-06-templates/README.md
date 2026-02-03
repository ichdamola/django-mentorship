# Week 06: Django Templates

## 🎯 Learning Objectives

By the end of this week, you will:

- Master Django Template Language (DTL) syntax
- Create reusable template layouts with inheritance
- Use template tags and filters effectively
- Build custom template tags and filters
- Organize templates properly in your project

## 📚 Required Reading

| Resource                                                                                  | Section   | Time   |
| ----------------------------------------------------------------------------------------- | --------- | ------ |
| [Django Templates](https://docs.djangoproject.com/en/5.0/topics/templates/)               | Full page | 30 min |
| [Built-in Tags & Filters](https://docs.djangoproject.com/en/5.0/ref/templates/builtins/)  | Reference | 45 min |
| [Custom Template Tags](https://docs.djangoproject.com/en/5.0/howto/custom-template-tags/) | Full page | 30 min |

---

## Part 1: Template Configuration

### Exercise 6.1: Set Up Templates Directory

Update your settings to include a project-level templates directory:

```python
# config/settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Project-level templates
        'APP_DIRS': True,  # Also look in app/templates/ directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

Create the directory structure:

```bash
# Create template directories
mkdir -p templates/includes
mkdir -p tasks/templates/tasks
```

Your project should look like this:

```
taskmaster/
├── config/
│   └── settings.py
├── templates/                    # Project-level templates
│   ├── base.html                # Master layout
│   ├── includes/                # Reusable partials
│   │   ├── _navbar.html
│   │   ├── _footer.html
│   │   ├── _messages.html
│   │   └── _pagination.html
│   └── 404.html                 # Error pages
├── tasks/
│   └── templates/
│       └── tasks/               # App-specific templates
│           ├── task_list.html
│           ├── task_detail.html
│           ├── task_form.html
│           └── task_confirm_delete.html
└── manage.py
```

---

## Part 2: Template Inheritance

### Exercise 6.2: Create Base Template

The base template defines the common structure for all pages.

Create `templates/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{% block title %}TaskMaster{% endblock %}</title>

    <!-- Bootstrap CSS -->
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />

    <!-- Custom CSS block for child templates -->
    {% block extra_css %}{% endblock %}

    <style>
      :root {
        --django-green: #092e20;
        --django-green-light: #44b78b;
      }
      body {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
      }
      .navbar {
        background-color: var(--django-green) !important;
      }
      .btn-primary {
        background-color: var(--django-green);
        border-color: var(--django-green);
      }
      .btn-primary:hover {
        background-color: #0a3d2e;
        border-color: #0a3d2e;
      }
      main {
        flex: 1;
      }
    </style>
  </head>
  <body>
    <!-- Navigation -->
    {% include "includes/_navbar.html" %}

    <!-- Flash Messages -->
    {% include "includes/_messages.html" %}

    <!-- Main Content -->
    <main class="container my-4">
      {% block content %}
      <!-- Child templates override this block -->
      {% endblock %}
    </main>

    <!-- Footer -->
    {% include "includes/_footer.html" %}

    <!-- Bootstrap JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Custom JS block for child templates -->
    {% block extra_js %}{% endblock %}
  </body>
</html>
```

---

### Exercise 6.3: Create Include Partials

Create `templates/includes/_navbar.html`:

```html
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container">
    <a class="navbar-brand" href="{% url 'tasks:dashboard' %}">
      🎯 TaskMaster
    </a>

    <button
      class="navbar-toggler"
      type="button"
      data-bs-toggle="collapse"
      data-bs-target="#navbarNav"
    >
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav me-auto">
        <li class="nav-item">
          <a
            class="nav-link {% if request.resolver_match.url_name == 'dashboard' %}active{% endif %}"
            href="{% url 'tasks:dashboard' %}"
          >
            Dashboard
          </a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link {% if 'task_list' in request.resolver_match.url_name %}active{% endif %}"
            href="{% url 'tasks:task_list' %}"
          >
            Tasks
          </a>
        </li>
      </ul>

      <a class="btn btn-outline-light" href="{% url 'tasks:task_create' %}">
        + New Task
      </a>
    </div>
  </div>
</nav>
```

Create `templates/includes/_messages.html`:

```html
{% if messages %}
<div class="container mt-3">
  {% for message in messages %}
  <div
    class="alert alert-{{ message.tags|default:'info' }} alert-dismissible fade show"
    role="alert"
  >
    {{ message }}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  </div>
  {% endfor %}
</div>
{% endif %}
```

Create `templates/includes/_footer.html`:

```html
<footer class="bg-light py-4 mt-auto">
  <div class="container text-center">
    <p class="text-muted mb-0">
      TaskMaster &copy; {% now "Y" %} | Built with Django
    </p>
  </div>
</footer>
```

Create `templates/includes/_pagination.html`:

```html
{% if page_obj.has_other_pages %}
<nav aria-label="Page navigation">
  <ul class="pagination justify-content-center">
    {% if page_obj.has_previous %}
    <li class="page-item">
      <a
        class="page-link"
        href="?page=1{% for key, value in request.GET.items %}{% if key != 'page' %}&{{ key }}={{ value }}{% endif %}{% endfor %}"
      >
        &laquo; First
      </a>
    </li>
    <li class="page-item">
      <a
        class="page-link"
        href="?page={{ page_obj.previous_page_number }}{% for key, value in request.GET.items %}{% if key != 'page' %}&{{ key }}={{ value }}{% endif %}{% endfor %}"
      >
        Previous
      </a>
    </li>
    {% endif %}

    <li class="page-item disabled">
      <span class="page-link">
        Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}
      </span>
    </li>

    {% if page_obj.has_next %}
    <li class="page-item">
      <a
        class="page-link"
        href="?page={{ page_obj.next_page_number }}{% for key, value in request.GET.items %}{% if key != 'page' %}&{{ key }}={{ value }}{% endif %}{% endfor %}"
      >
        Next
      </a>
    </li>
    <li class="page-item">
      <a
        class="page-link"
        href="?page={{ page_obj.paginator.num_pages }}{% for key, value in request.GET.items %}{% if key != 'page' %}&{{ key }}={{ value }}{% endif %}{% endfor %}"
      >
        Last &raquo;
      </a>
    </li>
    {% endif %}
  </ul>
</nav>
{% endif %}
```

---

## Part 3: App Templates

### Exercise 6.4: Create Task Templates

Create `tasks/templates/tasks/task_list.html`:

```html
{% extends "base.html" %}

{% block title %}Tasks - TaskMaster{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1>Tasks</h1>
    <a href="{% url 'tasks:task_create' %}" class="btn btn-primary">
        + New Task
    </a>
</div>

<!-- Filters -->
<div class="card mb-4">
    <div class="card-body">
        <form method="get" class="row g-3">
            <div class="col-md-4">
                <label class="form-label">Status</label>
                <select name="status" class="form-select">
                    <option value="">All Statuses</option>
                    {% for value, label in statuses %}
                    <option value="{{ value }}" {% if current_status == value %}selected{% endif %}>
                        {{ label }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-4">
                <label class="form-label">Category</label>
                <select name="category" class="form-select">
                    <option value="">All Categories</option>
                    {% for category in categories %}
                    <option value="{{ category.pk }}"
                            {% if current_category == category.pk|stringformat:"d" %}selected{% endif %}>
                        {{ category.name }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-4 d-flex align-items-end">
                <button type="submit" class="btn btn-outline-primary">Filter</button>
                <a href="{% url 'tasks:task_list' %}" class="btn btn-outline-secondary ms-2">
                    Clear
                </a>
            </div>
        </form>
    </div>
</div>

<!-- Task List -->
{% if page_obj %}
<div class="list-group mb-4">
    {% for task in page_obj %}
    <div class="list-group-item list-group-item-action">
        <div class="d-flex w-100 justify-content-between align-items-start">
            <div>
                <h5 class="mb-1">
                    <a href="{% url 'tasks:task_detail' pk=task.pk %}"
                       class="text-decoration-none">
                        {{ task.title }}
                    </a>
                </h5>
                <p class="mb-1 text-muted">
                    {% if task.category %}
                    <span class="badge" style="background-color: {{ task.category.color }}">
                        {{ task.category.name }}
                    </span>
                    {% endif %}

                    {% for tag in task.tags.all %}
                    <span class="badge bg-secondary">{{ tag.name }}</span>
                    {% endfor %}
                </p>
                {% if task.description %}
                <small class="text-muted">
                    {{ task.description|truncatewords:20 }}
                </small>
                {% endif %}
            </div>
            <div class="text-end">
                <!-- Status Badge -->
                <span class="badge
                    {% if task.status == 'completed' %}bg-success
                    {% elif task.status == 'in_progress' %}bg-warning text-dark
                    {% elif task.status == 'cancelled' %}bg-danger
                    {% else %}bg-secondary{% endif %}">
                    {{ task.get_status_display }}
                </span>

                <!-- Priority -->
                <div class="small text-muted mt-1">
                    Priority: {{ task.priority_display }}
                </div>

                <!-- Due Date -->
                {% if task.due_date %}
                <div class="small {% if task.is_overdue %}text-danger fw-bold{% else %}text-muted{% endif %}">
                    Due: {{ task.due_date|date:"M d, Y" }}
                    {% if task.is_overdue %}(Overdue!){% endif %}
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    {% endfor %}
</div>

<!-- Pagination -->
{% include "includes/_pagination.html" with page_obj=page_obj %}

{% else %}
<div class="alert alert-info">
    <p class="mb-0">
        No tasks found.
        <a href="{% url 'tasks:task_create' %}">Create your first task!</a>
    </p>
</div>
{% endif %}
{% endblock %}
```

Create `tasks/templates/tasks/task_detail.html`:

```html
{% extends "base.html" %} {% block title %}{{ task.title }} - TaskMaster{%
endblock %} {% block content %}
<nav aria-label="breadcrumb" class="mb-4">
  <ol class="breadcrumb">
    <li class="breadcrumb-item">
      <a href="{% url 'tasks:dashboard' %}">Dashboard</a>
    </li>
    <li class="breadcrumb-item">
      <a href="{% url 'tasks:task_list' %}">Tasks</a>
    </li>
    <li class="breadcrumb-item active">{{ task.title|truncatewords:5 }}</li>
  </ol>
</nav>

<div class="card">
  <div class="card-header d-flex justify-content-between align-items-center">
    <h1 class="h3 mb-0">{{ task.title }}</h1>
    <div>
      <a
        href="{% url 'tasks:task_update' pk=task.pk %}"
        class="btn btn-outline-primary btn-sm"
      >
        Edit
      </a>
      <a
        href="{% url 'tasks:task_delete' pk=task.pk %}"
        class="btn btn-outline-danger btn-sm"
      >
        Delete
      </a>
    </div>
  </div>
  <div class="card-body">
    <div class="row">
      <div class="col-md-8">
        <h5>Description</h5>
        <p>
          {{ task.description|default:"No description provided."|linebreaks }}
        </p>

        {% if task.tags.exists %}
        <h5>Tags</h5>
        <p>
          {% for tag in task.tags.all %}
          <span class="badge bg-secondary">{{ tag.name }}</span>
          {% endfor %}
        </p>
        {% endif %}
      </div>
      <div class="col-md-4">
        <div class="card bg-light">
          <div class="card-body">
            <p>
              <strong>Status:</strong><br />
              <span
                class="badge 
                                {% if task.status == 'completed' %}bg-success
                                {% elif task.status == 'in_progress' %}bg-warning text-dark
                                {% else %}bg-secondary{% endif %}"
              >
                {{ task.get_status_display }}
              </span>
            </p>

            <p>
              <strong>Priority:</strong><br />
              {{ task.priority_display }}
            </p>

            {% if task.category %}
            <p>
              <strong>Category:</strong><br />
              <span
                class="badge"
                style="background-color: {{ task.category.color }}"
              >
                {{ task.category.name }}
              </span>
            </p>
            {% endif %} {% if task.due_date %}
            <p>
              <strong>Due Date:</strong><br />
              <span class="{% if task.is_overdue %}text-danger{% endif %}">
                {{ task.due_date|date:"F d, Y" }} {% if task.is_overdue %}<br /><small
                  >(Overdue!)</small
                >{% endif %}
              </span>
            </p>
            {% endif %}

            <hr />

            <p class="small text-muted mb-1">
              <strong>Created:</strong> {{ task.created_at|date:"M d, Y H:i" }}
            </p>
            <p class="small text-muted mb-0">
              <strong>Updated:</strong> {{ task.updated_at|date:"M d, Y H:i" }}
            </p>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="mt-3">
          {% if task.status != 'completed' %}
          <form
            method="post"
            action="{% url 'tasks:task_complete' pk=task.pk %}"
          >
            {% csrf_token %}
            <button type="submit" class="btn btn-success w-100">
              ✓ Mark Complete
            </button>
          </form>
          {% endif %}
        </div>
      </div>
    </div>
  </div>
</div>

<div class="mt-3">
  <a href="{% url 'tasks:task_list' %}" class="btn btn-outline-secondary">
    ← Back to Tasks
  </a>
</div>
{% endblock %}
```

Create `tasks/templates/tasks/task_form.html`:

```html
{% extends "base.html" %} {% block title %} {% if form.instance.pk %}Edit Task{%
else %}Create Task{% endif %} - TaskMaster {% endblock %} {% block content %}
<div class="row justify-content-center">
  <div class="col-md-8">
    <div class="card">
      <div class="card-header">
        <h1 class="h4 mb-0">
          {% if form.instance.pk %} Edit Task: {{ form.instance.title }} {% else
          %} Create New Task {% endif %}
        </h1>
      </div>
      <div class="card-body">
        <form method="post" novalidate>
          {% csrf_token %} {% if form.non_field_errors %}
          <div class="alert alert-danger">
            {% for error in form.non_field_errors %}
            <p class="mb-0">{{ error }}</p>
            {% endfor %}
          </div>
          {% endif %} {% for field in form %}
          <div class="mb-3">
            <label for="{{ field.id_for_label }}" class="form-label">
              {{ field.label }} {% if field.field.required %}
              <span class="text-danger">*</span>
              {% endif %}
            </label>

            {% if field.field.widget.input_type == 'checkbox' %} {{ field }} {%
            else %} {{ field }} {% endif %} {% if field.errors %}
            <div class="invalid-feedback d-block">
              {% for error in field.errors %}{{ error }}{% endfor %}
            </div>
            {% endif %} {% if field.help_text %}
            <small class="form-text text-muted">{{ field.help_text }}</small>
            {% endif %}
          </div>
          {% endfor %}

          <div class="d-flex gap-2">
            <button type="submit" class="btn btn-primary">
              {% if form.instance.pk %}Update{% else %}Create{% endif %} Task
            </button>
            <a
              href="{% url 'tasks:task_list' %}"
              class="btn btn-outline-secondary"
            >
              Cancel
            </a>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %} {% block extra_css %}
<style>
  /* Style form fields with Bootstrap classes */
  .form-control,
  .form-select {
    /* Applied via widget attrs in forms.py ideally */
  }
</style>
{% endblock %}
```

Create `tasks/templates/tasks/task_confirm_delete.html`:

```html
{% extends "base.html" %} {% block title %}Delete Task - TaskMaster{% endblock
%} {% block content %}
<div class="row justify-content-center">
  <div class="col-md-6">
    <div class="card border-danger">
      <div class="card-header bg-danger text-white">
        <h1 class="h4 mb-0">Delete Task</h1>
      </div>
      <div class="card-body">
        <p class="lead">Are you sure you want to delete this task?</p>

        <div class="card bg-light mb-4">
          <div class="card-body">
            <h5>{{ task.title }}</h5>
            {% if task.description %}
            <p class="text-muted mb-0">
              {{ task.description|truncatewords:30 }}
            </p>
            {% endif %}
          </div>
        </div>

        <p class="text-danger">
          <strong>Warning:</strong> This action cannot be undone.
        </p>

        <form method="post">
          {% csrf_token %}
          <div class="d-flex gap-2">
            <button type="submit" class="btn btn-danger">
              Yes, Delete Task
            </button>
            <a
              href="{% url 'tasks:task_detail' pk=task.pk %}"
              class="btn btn-outline-secondary"
            >
              Cancel
            </a>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

Create `tasks/templates/tasks/dashboard.html`:

```html
{% extends "base.html" %} {% block title %}Dashboard - TaskMaster{% endblock %}
{% block content %}
<h1 class="mb-4">Dashboard</h1>

<!-- Stats Cards -->
<div class="row mb-4">
  <div class="col-md-3">
    <div class="card text-center">
      <div class="card-body">
        <h2 class="display-4">{{ total_tasks }}</h2>
        <p class="text-muted mb-0">Total Tasks</p>
      </div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="card text-center border-success">
      <div class="card-body">
        <h2 class="display-4 text-success">{{ completed_tasks }}</h2>
        <p class="text-muted mb-0">Completed</p>
      </div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="card text-center border-warning">
      <div class="card-body">
        <h2 class="display-4 text-warning">{{ in_progress_tasks }}</h2>
        <p class="text-muted mb-0">In Progress</p>
      </div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="card text-center border-secondary">
      <div class="card-body">
        <h2 class="display-4 text-secondary">{{ pending_tasks }}</h2>
        <p class="text-muted mb-0">Pending</p>
      </div>
    </div>
  </div>
</div>

<!-- Categories -->
<div class="row">
  <div class="col-md-6">
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">Tasks by Category</h5>
      </div>
      <ul class="list-group list-group-flush">
        {% for category in categories %}
        <li
          class="list-group-item d-flex justify-content-between align-items-center"
        >
          <span>
            <span
              class="badge me-2"
              style="background-color: {{ category.color }}"
            >
              &nbsp;
            </span>
            {{ category.name }}
          </span>
          <span class="badge bg-primary rounded-pill">
            {{ category.task_count }}
          </span>
        </li>
        {% empty %}
        <li class="list-group-item text-muted">No categories yet</li>
        {% endfor %}
      </ul>
    </div>
  </div>

  <div class="col-md-6">
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">Recent Tasks</h5>
      </div>
      <ul class="list-group list-group-flush">
        {% for task in recent_tasks %}
        <li class="list-group-item">
          <a
            href="{% url 'tasks:task_detail' pk=task.pk %}"
            class="text-decoration-none"
          >
            {{ task.title }}
          </a>
          <small class="text-muted float-end">
            {{ task.created_at|timesince }} ago
          </small>
        </li>
        {% empty %}
        <li class="list-group-item text-muted">No tasks yet</li>
        {% endfor %}
      </ul>
    </div>
  </div>
</div>
{% endblock %}
```

---

## Part 4: Template Tags and Filters

### Common Built-in Filters

```
┌─────────────────────────────────────────────────────────────────┐
│                    Common Template Filters                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TEXT FILTERS                                                    │
│  {{ text|lower }}              → lowercase                       │
│  {{ text|upper }}              → UPPERCASE                       │
│  {{ text|title }}              → Title Case                      │
│  {{ text|truncatewords:10 }}   → First 10 words...              │
│  {{ text|truncatechars:50 }}   → First 50 chars...              │
│  {{ text|linebreaks }}         → <p> tags for newlines          │
│  {{ text|striptags }}          → Remove HTML tags                │
│  {{ text|slugify }}            → url-friendly-slug               │
│                                                                  │
│  NUMBER FILTERS                                                  │
│  {{ num|add:5 }}               → num + 5                         │
│  {{ price|floatformat:2 }}     → 19.99                          │
│  {{ count|pluralize }}         → "s" if count != 1              │
│  {{ bytes|filesizeformat }}    → "1.5 MB"                       │
│                                                                  │
│  DATE FILTERS                                                    │
│  {{ date|date:"M d, Y" }}      → Jan 15, 2024                   │
│  {{ date|time:"H:i" }}         → 14:30                          │
│  {{ date|timesince }}          → 3 days ago                     │
│  {{ date|timeuntil }}          → in 2 weeks                     │
│                                                                  │
│  LIST FILTERS                                                    │
│  {{ list|length }}             → count of items                  │
│  {{ list|first }}              → first item                      │
│  {{ list|last }}               → last item                       │
│  {{ list|join:", " }}          → "a, b, c"                      │
│  {{ list|slice:":5" }}         → first 5 items                  │
│                                                                  │
│  DEFAULT VALUES                                                  │
│  {{ value|default:"N/A" }}     → "N/A" if falsy                 │
│  {{ value|default_if_none:"" }} → "" if None                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Common Built-in Tags

```html
<!-- Conditionals -->
{% if condition %} ... {% elif other_condition %} ... {% else %} ... {% endif %}

<!-- Loops -->
{% for item in list %} {{ forloop.counter }} {# 1-indexed counter #} {{
forloop.counter0 }} {# 0-indexed counter #} {{ forloop.first }} {# True if first
iteration #} {{ forloop.last }} {# True if last iteration #} {% empty %} No
items found. {% endfor %}

<!-- URL Generation -->
{% url 'app:view_name' %} {% url 'app:view_name' pk=object.pk %} {% url
'app:view_name' as the_url %}

<!-- Static Files -->
{% load static %}
<img src="{% static 'images/logo.png' %}" />

<!-- CSRF Token (required for forms) -->
<form method="post">{% csrf_token %}</form>

<!-- Include Templates -->
{% include "partial.html" %} {% include "partial.html" with variable=value %}

<!-- Template Inheritance -->
{% extends "base.html" %} {% block content %}...{% endblock %}

<!-- Comments -->
{# Single line comment #} {% comment %} Multi-line comment {% endcomment %}

<!-- Current Date/Time -->
{% now "Y-m-d" %}
```

---

## Part 5: Custom Template Tags

### Exercise 6.5: Create Custom Tags and Filters

Create the templatetags directory:

```bash
mkdir -p tasks/templatetags
touch tasks/templatetags/__init__.py
```

Create `tasks/templatetags/task_extras.py`:

```python
"""
Custom template tags and filters for the tasks app.

Usage in templates:
    {% load task_extras %}
    {{ task.status|status_badge }}
    {% task_stats as stats %}
"""

from django import template
from django.utils.html import format_html
from django.db.models import Count

from tasks.models import Task, Status

register = template.Library()


# ============================================================
# FILTERS
# ============================================================

@register.filter
def status_badge(status: str) -> str:
    """
    Return a Bootstrap badge class based on task status.

    Usage: {{ task.status|status_badge }}
    """
    badge_classes = {
        'completed': 'bg-success',
        'in_progress': 'bg-warning text-dark',
        'pending': 'bg-secondary',
        'cancelled': 'bg-danger',
    }
    return badge_classes.get(status, 'bg-secondary')


@register.filter
def priority_stars(priority: int) -> str:
    """
    Display priority as stars.

    Usage: {{ task.priority|priority_stars }}
    """
    return '★' * priority + '☆' * (4 - priority)


@register.filter
def percentage(value, total):
    """
    Calculate percentage.

    Usage: {{ completed|percentage:total }}
    """
    try:
        return int((value / total) * 100)
    except (ValueError, ZeroDivisionError):
        return 0


# ============================================================
# SIMPLE TAGS
# ============================================================

@register.simple_tag
def task_count(status: str = None) -> int:
    """
    Get count of tasks, optionally filtered by status.

    Usage:
        {% task_count as total %}
        {% task_count 'completed' as completed %}
    """
    if status:
        return Task.objects.filter(status=status).count()
    return Task.objects.count()


@register.simple_tag(takes_context=True)
def active_link(context, url_name: str) -> str:
    """
    Return 'active' if current URL matches.

    Usage: <a class="nav-link {% active_link 'tasks:task_list' %}">
    """
    request = context.get('request')
    if request and request.resolver_match:
        if request.resolver_match.url_name == url_name:
            return 'active'
    return ''


# ============================================================
# INCLUSION TAGS
# ============================================================

@register.inclusion_tag('tasks/_task_card.html')
def task_card(task):
    """
    Render a task card component.

    Usage: {% task_card task %}
    """
    return {'task': task}


@register.inclusion_tag('tasks/_task_stats.html')
def task_stats():
    """
    Render task statistics.

    Usage: {% task_stats %}
    """
    return {
        'total': Task.objects.count(),
        'completed': Task.objects.filter(status=Status.COMPLETED).count(),
        'pending': Task.objects.filter(status=Status.PENDING).count(),
        'in_progress': Task.objects.filter(status=Status.IN_PROGRESS).count(),
    }


# ============================================================
# ASSIGNMENT TAGS
# ============================================================

@register.simple_tag
def get_categories_with_counts():
    """
    Get all categories with their task counts.

    Usage: {% get_categories_with_counts as categories %}
    """
    from tasks.models import Category
    return Category.objects.annotate(task_count=Count('tasks'))
```

Create `tasks/templates/tasks/_task_card.html`:

```html
<div class="card h-100">
  <div class="card-body">
    <h5 class="card-title">
      <a
        href="{% url 'tasks:task_detail' pk=task.pk %}"
        class="text-decoration-none"
      >
        {{ task.title }}
      </a>
    </h5>
    <p class="card-text text-muted">
      {{ task.description|default:"No description"|truncatewords:15 }}
    </p>
  </div>
  <div class="card-footer bg-transparent">
    <span class="badge {{ task.status|status_badge }}">
      {{ task.get_status_display }}
    </span>
    <small class="text-muted float-end">
      {{ task.created_at|timesince }} ago
    </small>
  </div>
</div>
```

---

## 📝 Weekly Project: Complete Template System

Your task is to create all templates for TaskMaster with:

1. **Base template** with proper inheritance structure
2. **All CRUD templates** for tasks
3. **Dashboard** with statistics
4. **Custom template tags** for reusable components
5. **Proper use of includes** for partials

### Requirements:

- [ ] `base.html` with blocks for title, content, css, js
- [ ] `_navbar.html` with active link highlighting
- [ ] `_footer.html` with current year
- [ ] `_messages.html` for flash messages
- [ ] `_pagination.html` that preserves query params
- [ ] `task_list.html` with filtering and pagination
- [ ] `task_detail.html` with all task info
- [ ] `task_form.html` for create/edit
- [ ] `task_confirm_delete.html`
- [ ] `dashboard.html` with stats
- [ ] Custom `status_badge` filter
- [ ] Custom `task_card` inclusion tag

---

## 📋 Submission Checklist

- [ ] Template directory structure correct
- [ ] Base template with inheritance working
- [ ] All CRUD templates implemented
- [ ] Includes used for navbar, footer, messages
- [ ] Pagination preserves filter params
- [ ] Custom template tags created and working
- [ ] No `TemplateDoesNotExist` errors
- [ ] Templates pass HTML validation

---

## 🔗 Additional Resources

- [Django Template Language](https://docs.djangoproject.com/en/5.0/ref/templates/language/)
- [Built-in Template Tags](https://docs.djangoproject.com/en/5.0/ref/templates/builtins/)
- [Custom Template Tags](https://docs.djangoproject.com/en/5.0/howto/custom-template-tags/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)

---

**Next**: [Week 07: Forms →](../week-07-forms/README.md)
