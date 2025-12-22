# Week 11: Testing Django Applications

## 🎯 Learning Objectives

- Write unit tests with pytest
- Use fixtures for test data
- Test models, views, and forms
- Mock external dependencies
- Achieve high test coverage

## 📚 Required Reading

| Resource                                                                | Section         | Time   |
| ----------------------------------------------------------------------- | --------------- | ------ |
| [Django Testing](https://docs.djangoproject.com/en/5.0/topics/testing/) | Full page       | 45 min |
| [pytest-django](https://pytest-django.readthedocs.io/)                  | Getting started | 30 min |
| [Factory Boy](https://factoryboy.readthedocs.io/)                       | Tutorial        | 20 min |

---

## Setup

```bash
uv add --dev pytest pytest-django pytest-cov factory-boy
```

```python
# pyproject.toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
python_files = ["test_*.py", "*_test.py"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["tasks"]
omit = ["*/migrations/*", "*/tests/*"]
```

---

## Key Concepts

### Factories

```python
# tasks/tests/factories.py
import factory
from factory.django import DjangoModelFactory
from tasks.models import Task, Category, Tag, Priority, Status


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Category {n}')
    description = factory.Faker('text', max_nb_chars=200)
    color = factory.Faker('hex_color')


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f'tag-{n}')


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph')
    priority = Priority.MEDIUM
    status = Status.PENDING
    category = factory.SubFactory(CategoryFactory)
    owner = factory.SubFactory('accounts.tests.factories.UserFactory')

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)
```

### Model Tests

```python
# tasks/tests/test_models.py
import pytest
from django.utils import timezone
from datetime import timedelta

from tasks.models import Task, Status
from .factories import TaskFactory, CategoryFactory


@pytest.mark.django_db
class TestTaskModel:
    def test_create_task(self):
        task = TaskFactory()
        assert task.pk is not None
        assert task.status == Status.PENDING

    def test_mark_complete(self):
        task = TaskFactory(status=Status.PENDING)
        task.mark_complete()

        assert task.status == Status.COMPLETED
        assert task.completed_at is not None

    def test_is_overdue_when_past_due(self):
        task = TaskFactory(
            due_date=timezone.now().date() - timedelta(days=1),
            status=Status.PENDING
        )
        assert task.is_overdue is True

    def test_is_not_overdue_when_completed(self):
        task = TaskFactory(
            due_date=timezone.now().date() - timedelta(days=1),
            status=Status.COMPLETED
        )
        assert task.is_overdue is False

    def test_str_returns_title(self):
        task = TaskFactory(title="Test Task")
        assert str(task) == "Test Task"
```

### View Tests

```python
# tasks/tests/test_views.py
import pytest
from django.urls import reverse
from rest_framework import status as http_status

from .factories import TaskFactory, UserFactory


@pytest.mark.django_db
class TestTaskListView:
    def test_list_requires_auth(self, client):
        url = reverse('tasks:task_list')
        response = client.get(url)

        assert response.status_code == 302
        assert '/login/' in response.url

    def test_list_shows_user_tasks_only(self, client):
        user = UserFactory()
        other_user = UserFactory()

        my_task = TaskFactory(owner=user, title="My Task")
        other_task = TaskFactory(owner=other_user, title="Other Task")

        client.force_login(user)
        response = client.get(reverse('tasks:task_list'))

        assert response.status_code == 200
        assert "My Task" in response.content.decode()
        assert "Other Task" not in response.content.decode()


@pytest.mark.django_db
class TestTaskAPI:
    def test_create_task(self, api_client, user):
        api_client.force_authenticate(user)

        data = {
            'title': 'New Task',
            'description': 'Task description',
            'priority': 2,
        }

        response = api_client.post('/api/v1/tasks/', data)

        assert response.status_code == http_status.HTTP_201_CREATED
        assert response.data['title'] == 'New Task'
        assert response.data['owner'] == str(user)
```

### Fixtures

```python
# conftest.py
import pytest
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(client, user):
    client.force_login(user)
    return client
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=tasks --cov-report=html

# Run specific test file
uv run pytest tasks/tests/test_models.py

# Run specific test
uv run pytest tasks/tests/test_models.py::TestTaskModel::test_mark_complete

# Verbose output
uv run pytest -v
```

---

## 📋 Submission Checklist

- [ ] pytest configured
- [ ] Factories for all models
- [ ] Model tests (CRUD, methods, properties)
- [ ] View tests (permissions, rendering)
- [ ] API tests (all endpoints)
- [ ] 80%+ test coverage

---

**Next**: [Week 12: Advanced ORM →](../week-12-advanced-orm/README.md)
