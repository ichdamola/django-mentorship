# Week 12: Advanced ORM Techniques

## 🎯 Learning Objectives

- Optimize queries with select_related and prefetch_related
- Use aggregations and annotations
- Write complex queries with Q and F objects
- Implement raw SQL when needed
- Profile and debug database queries

## 📚 Required Reading

| Resource                                                                            | Section        | Time   |
| ----------------------------------------------------------------------------------- | -------------- | ------ |
| [QuerySet API](https://docs.djangoproject.com/en/5.0/ref/models/querysets/)         | Full reference | 60 min |
| [Aggregation](https://docs.djangoproject.com/en/5.0/topics/db/aggregation/)         | Full page      | 30 min |
| [Query Optimization](https://docs.djangoproject.com/en/5.0/topics/db/optimization/) | Full page      | 30 min |

---

## Key Concepts

### Query Optimization

```python
# BAD: N+1 query problem
tasks = Task.objects.all()
for task in tasks:
    print(task.category.name)  # Each access hits database!

# GOOD: select_related for ForeignKey
tasks = Task.objects.select_related('category').all()
for task in tasks:
    print(task.category.name)  # No additional queries!

# GOOD: prefetch_related for ManyToMany
tasks = Task.objects.prefetch_related('tags').all()
for task in tasks:
    print([t.name for t in task.tags.all()])  # Already fetched!

# Combined
tasks = Task.objects.select_related('category', 'owner').prefetch_related('tags')
```

### Aggregations

```python
from django.db.models import Count, Avg, Sum, Max, Min, Q, F

# Basic aggregation
Task.objects.aggregate(
    total=Count('id'),
    avg_priority=Avg('priority'),
)

# Conditional aggregation
Task.objects.aggregate(
    total=Count('id'),
    completed=Count('id', filter=Q(status='completed')),
    high_priority=Count('id', filter=Q(priority__gte=3)),
)

# Group by with annotation
Category.objects.annotate(
    task_count=Count('tasks'),
    completed_count=Count('tasks', filter=Q(tasks__status='completed')),
).values('name', 'task_count', 'completed_count')

# Computed fields
Task.objects.annotate(
    days_until_due=F('due_date') - timezone.now().date()
).filter(days_until_due__lte=7)
```

### Complex Queries

```python
from django.db.models import Q, F, Case, When, Value

# OR conditions
Task.objects.filter(
    Q(priority=Priority.HIGH) | Q(status=Status.OVERDUE)
)

# NOT conditions
Task.objects.filter(~Q(status=Status.COMPLETED))

# Dynamic filtering
def search_tasks(query=None, status=None, category=None):
    filters = Q()
    if query:
        filters &= Q(title__icontains=query) | Q(description__icontains=query)
    if status:
        filters &= Q(status=status)
    if category:
        filters &= Q(category_id=category)
    return Task.objects.filter(filters)

# Conditional expressions
Task.objects.annotate(
    priority_label=Case(
        When(priority=1, then=Value('Low')),
        When(priority=2, then=Value('Medium')),
        When(priority=3, then=Value('High')),
        default=Value('Unknown'),
    )
)

# Subqueries
from django.db.models import Subquery, OuterRef

latest_task = Task.objects.filter(
    category=OuterRef('pk')
).order_by('-created_at')

Category.objects.annotate(
    latest_task_title=Subquery(latest_task.values('title')[:1])
)
```

### Query Debugging

```python
# Print SQL
print(Task.objects.filter(status='pending').query)

# Django Debug Toolbar (install in dev)
# uv add --dev django-debug-toolbar

# Query counting in tests
from django.test.utils import CaptureQueriesContext
from django.db import connection

with CaptureQueriesContext(connection) as context:
    list(Task.objects.select_related('category').all())

print(f"Number of queries: {len(context)}")
for query in context:
    print(query['sql'])
```

### Raw SQL

```python
# Raw queryset (returns model instances)
Task.objects.raw('''
    SELECT * FROM tasks_task
    WHERE priority >= %s
    ORDER BY created_at DESC
''', [3])

# Direct cursor (for complex queries)
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute('''
        SELECT category_id, COUNT(*) as count
        FROM tasks_task
        GROUP BY category_id
    ''')
    results = cursor.fetchall()
```

---

## 📋 Submission Checklist

- [ ] Optimized queries with select_related/prefetch_related
- [ ] Dashboard with aggregated statistics
- [ ] Complex search with Q objects
- [ ] Query count verification in tests
- [ ] Debug toolbar configured

---

**Next**: [Week 13: Caching & Performance →](../week-13-caching-performance/README.md)
