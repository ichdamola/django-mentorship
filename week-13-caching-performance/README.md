# Week 13: Caching & Performance

## 🎯 Learning Objectives

- Implement caching with Redis
- Use Django's caching framework
- Cache views, templates, and querysets
- Profile and optimize application performance
- Implement database connection pooling

## 📚 Required Reading

| Resource                                                                              | Section   | Time   |
| ------------------------------------------------------------------------------------- | --------- | ------ |
| [Django Caching](https://docs.djangoproject.com/en/5.0/topics/cache/)                 | Full page | 45 min |
| [Performance Optimization](https://docs.djangoproject.com/en/5.0/topics/performance/) | Full page | 30 min |

---

## Setup Redis

```bash
# Install Redis client
uv add django-redis

# Docker for local Redis
docker run -d -p 6379:6379 --name redis redis:alpine
```

```python
# config/settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session backend (optional)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

---

## Key Concepts

### View Caching

```python
from django.views.decorators.cache import cache_page, cache_control
from django.utils.decorators import method_decorator

# Cache entire view for 15 minutes
@cache_page(60 * 15)
def task_list(request):
    ...

# Cache with cache control headers
@cache_control(private=True, max_age=300)
def user_dashboard(request):
    ...

# Class-based views
@method_decorator(cache_page(60 * 15), name='dispatch')
class TaskListView(ListView):
    ...

# Per-user caching
@cache_page(60 * 15, key_prefix='user')
def user_tasks(request):
    ...
```

### Low-Level Cache API

```python
from django.core.cache import cache

# Set and get
cache.set('my_key', 'my_value', timeout=300)
value = cache.get('my_key', default='default_value')

# Get or set
def get_expensive_data():
    return Task.objects.count()

count = cache.get_or_set('task_count', get_expensive_data, timeout=60)

# Delete
cache.delete('my_key')

# Multiple keys
cache.set_many({'key1': 'val1', 'key2': 'val2'})
values = cache.get_many(['key1', 'key2'])
cache.delete_many(['key1', 'key2'])

# Increment/decrement
cache.set('counter', 0)
cache.incr('counter')
cache.decr('counter')
```

### Caching Querysets

```python
from django.core.cache import cache

def get_categories():
    cache_key = 'all_categories'
    categories = cache.get(cache_key)

    if categories is None:
        categories = list(Category.objects.all())
        cache.set(cache_key, categories, timeout=3600)

    return categories

# Invalidate on save
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver([post_save, post_delete], sender=Category)
def invalidate_category_cache(sender, **kwargs):
    cache.delete('all_categories')
```

### Template Fragment Caching

```html
{% load cache %} {% cache 500 sidebar request.user.id %}
<!-- Expensive template fragment -->
{% for category in categories %}
<div>{{ category.name }}: {{ category.task_count }}</div>
{% endfor %} {% endcache %}
```

### Database Optimization

```python
# Connection pooling with dj-database-url
uv add dj-database-url psycopg2-binary

# config/settings.py
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='postgres://user:pass@localhost/dbname',
        conn_max_age=600,  # Connection pooling
    )
}

# Persistent connections
DATABASES['default']['CONN_MAX_AGE'] = 600
```

### Performance Profiling

```python
# Install django-silk for profiling
uv add --dev django-silk

# config/settings.py
INSTALLED_APPS += ['silk']
MIDDLEWARE += ['silk.middleware.SilkyMiddleware']

# config/urls.py
urlpatterns += [path('silk/', include('silk.urls'))]
```

---

## 📋 Submission Checklist

- [ ] Redis configured and running
- [ ] View caching implemented
- [ ] Low-level caching for expensive queries
- [ ] Cache invalidation on data changes
- [ ] Template fragment caching
- [ ] Query optimization verified

---

**Next**: [Week 14: Celery & Async →](../week-14-celery-async/README.md)
