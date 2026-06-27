# Week 13: Caching & Performance

## 🎯 Learning Objectives

- Implement caching with Redis
- Use Django's caching framework
- Cache views, templates, and querysets
- Profile and optimize application performance
- Implement database connection pooling

The cache-aside pattern you'll implement - hit Redis first, fall back to PostgreSQL and warm the cache on miss:

```mermaid
---
config:
  look: handDrawn
  theme: neutral
---
flowchart TB
    Request([Request])
    Check{"In Redis?"}
    Hit[Return cached value]
    DB[("PostgreSQL<br/>query")]
    Store[Store in Redis]
    Response([Response])

    Request --> Check
    Check -->|hit| Hit --> Response
    Check -->|miss| DB --> Store --> Response
```

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
# For production, prefer `cached_db` over `cache` - Redis restarts otherwise
# log every active user out. cached_db reads from cache, falls back to DB,
# writes to both.
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
```

---

## Key Concepts

### View Caching

```python
from django.views.decorators.cache import cache_page, cache_control
from django.views.decorators.vary import vary_on_cookie
from django.utils.decorators import method_decorator

# 🚨 NEVER do this on a user-scoped view:
#   @cache_page(60 * 15)
#   def task_list(request):
#       return ...filter(owner=request.user)
# `cache_page` keys on URL + a few headers - NOT on request.user. The first
# user's response is served to everyone else for 15 minutes. Privacy disaster.

# ✅ Safe: cache_page is fine on PUBLIC views (homepage, marketing pages,
# public catalogue) where the response doesn't depend on who's logged in.
@cache_page(60 * 15)
def public_homepage(request):
    ...

# ✅ For per-user caching, use the low-level cache API with user.id in the
# key (see "Low-Level Cache API" below). cache_page + vary_on_cookie works
# in theory but the cache hit rate collapses because each session cookie is
# unique - you're paying cache storage without amortizing across users.
@cache_control(private=True, max_age=300)   # browser cache only; never server-cache
def user_dashboard(request):
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
# Cache stampede / thundering herd: when a hot key expires, N concurrent
# requests all miss simultaneously and all run `get_expensive_data()`.
# For high-traffic keys, add jittered expiry (`timeout + random.randint(0, 60)`)
# or use a distributed lock (`from redis import Redis; r.set(..., nx=True, ex=...)`)
# so only one worker repopulates while the rest wait.

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
# Persistent connections vs. real pooling
uv add dj-database-url 'psycopg[binary]'

# config/settings.py
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='postgres://user:pass@localhost/dbname',
        conn_max_age=600,  # PERSISTENT connections - keeps each worker's
                           # connection alive for 600s between requests
                           # instead of opening/closing per request.
    )
}
```

> ⚠️ **CONN_MAX_AGE is not connection pooling - it's persistent connections.** They're related but distinct:
>
> - **Persistent connections (`CONN_MAX_AGE`):** each Gunicorn/uWSGI worker keeps *one* DB connection open across requests. Cheap. Built into Django. Avoids the per-request connect/auth/SSL overhead.
> - **Real connection pooling:** a shared pool that multiple workers/processes draw from. Provided by **PgBouncer** (external process) or **Django 5.1+'s `OPTIONS={'pool': True}`** (in-process via psycopg3). Crucial when you have *many* workers and Postgres' `max_connections` limit becomes a bottleneck.
>
> For a single-host blog, `CONN_MAX_AGE=600` is enough. For multi-host production with 50+ Gunicorn workers per host, add PgBouncer in front.

### Performance Profiling

```python
# Install django-silk for profiling
uv add --dev django-silk

# config/settings.py - dev only
if DEBUG:
    INSTALLED_APPS += ['silk']
    MIDDLEWARE += ['silk.middleware.SilkyMiddleware']
    # Restrict the silk UI to superusers (Silk records ALL SQL + request
    # bodies + headers including auth tokens; do NOT expose to anonymous
    # or staff-tier users):
    SILKY_AUTHENTICATION = True
    SILKY_AUTHORISATION = True
    SILKY_PERMISSIONS = lambda user: user.is_superuser

# config/urls.py
if settings.DEBUG:
    urlpatterns += [path('silk/', include('silk.urls'))]
```

> 🚨 **Never deploy Silk-enabled middleware to production.** It logs every
> request including bodies + auth headers. Same risk class as Debug Toolbar
> in production.

---

## 📋 Submission Checklist

- [ ] Redis configured and running
- [ ] View caching implemented
- [ ] Low-level caching for expensive queries
- [ ] Cache invalidation on data changes
- [ ] Template fragment caching
- [ ] Query optimization verified

---

**Next**: [Week 14: Celery & Async →](../week-14-celery-async/readme.md)
