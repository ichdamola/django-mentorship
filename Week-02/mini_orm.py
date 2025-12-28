"""
Mini ORM Project - Understanding Django's internals.

Build a simplified ORM that supports:
1. Model definition with typed fields
2. Validation
3. CRUD operations (in-memory)
4. Simple querying with filtering
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, TypeVar, Generic, Callable, ClassVar
from abc import ABC, abstractmethod


# Type variable for generic model operations
M = TypeVar("M", bound="Model")


# Fields


class Field(ABC):
    """Base field class with validation."""

    def __init__(
        self,
        required: bool = True,
        default: Any = None,
        validators: list[Callable[[Any], None]] | None = None,
    ):
        self.required = required
        self.default = default
        self.validators = validators or []
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    @abstractmethod
    def to_python(self, value: Any) -> Any:
        """Convert to Python type."""
        pass

    def validate(self, value: Any) -> None:
        """Run all validators."""
        if value is None:
            if self.required and self.default is None:
                raise ValueError(f"{self.name}: This field is required")
            return

        for validator in self.validators:
            validator(value)


class CharField(Field):
    def __init__(self, max_length: int = 255, min_length: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length
        self.min_length = min_length

    def to_python(self, value: Any) -> str | None:
        if value is None:
            return self.default
        return str(value)

    def validate(self, value: Any) -> None:
        super().validate(value)
        if value is not None:
            if len(value) > self.max_length:
                raise ValueError(f"{self.name}: Max length is {self.max_length}")
            if len(value) < self.min_length:
                raise ValueError(f"{self.name}: Min length is {self.min_length}")


class IntegerField(Field):
    def __init__(
        self, min_value: int | None = None, max_value: int | None = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def to_python(self, value: Any) -> int | None:
        if value is None:
            return self.default
        return int(value)

    def validate(self, value: Any) -> None:
        super().validate(value)
        if value is not None:
            if self.min_value is not None and value < self.min_value:
                raise ValueError(f"{self.name}: Must be >= {self.min_value}")
            if self.max_value is not None and value > self.max_value:
                raise ValueError(f"{self.name}: Must be <= {self.max_value}")


class BooleanField(Field):
    def to_python(self, value: Any) -> bool | None:
        if value is None:
            return self.default
        return bool(value)


class DateTimeField(Field):
    def __init__(self, auto_now: bool = False, auto_now_add: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add

    def to_python(self, value: Any) -> datetime | None:
        if value is None:
            return self.default
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value


# QuerySet

class QuerySet(Generic[M]):
    """
    Lazy query builder - like Django's QuerySet.
    Operations return new QuerySet, only execute on iteration.
    """

    def __init__(self, model_class: type[M], storage: "Storage"):
        self.model_class = model_class
        self.storage = storage
        self._filters: list[Callable[[M], bool]] = []
        self._order_by: str | None = None
        self._limit: int | None = None

    def _clone(self) -> "QuerySet[M]":
        """Return copy for chaining."""
        qs = QuerySet(self.model_class, self.storage)
        qs._filters = self._filters.copy()
        qs._order_by = self._order_by
        qs._limit = self._limit
        return qs

    def filter(self, **kwargs) -> "QuerySet[M]":
        """Filter by field values."""
        qs = self._clone()
        for field_name, value in kwargs.items():
            qs._filters.append(lambda obj, f=field_name, v=value: getattr(obj, f) == v)
        return qs

    def exclude(self, **kwargs) -> "QuerySet[M]":
        """Exclude by field values."""
        qs = self._clone()
        for field_name, value in kwargs.items():
            qs._filters.append(lambda obj, f=field_name, v=value: getattr(obj, f) != v)
        return qs

    def order_by(self, field_name: str) -> "QuerySet[M]":
        """Order results by field."""
        qs = self._clone()
        qs._order_by = field_name
        return qs

    def limit(self, count: int) -> "QuerySet[M]":
        """Limit number of results."""
        qs = self._clone()
        qs._limit = count
        return qs

    def _execute(self) -> list[M]:
        """Execute query and return results."""
        table_name = self.model_class.__name__.lower()
        results = list(self.storage.tables.get(table_name, {}).values())

        # Apply filters
        for filter_func in self._filters:
            results = [obj for obj in results if filter_func(obj)]

        # Apply ordering
        if self._order_by:
            reverse = self._order_by.startswith("-")
            field = self._order_by.lstrip("-")
            results.sort(key=lambda x: getattr(x, field), reverse=reverse)

        # Apply limit
        if self._limit:
            results = results[: self._limit]

        return results

    def all(self) -> list[M]:
        """Get all matching records."""
        return self._execute()

    def first(self) -> M | None:
        """Get first matching record."""
        results = self.limit(1)._execute()
        return results[0] if results else None

    def count(self) -> int:
        """Count matching records."""
        return len(self._execute())

    def exists(self) -> bool:
        """Check if any records match."""
        return self.count() > 0

    def __iter__(self):
        return iter(self._execute())

    def __len__(self):
        return self.count()


# Manager


class Manager(Generic[M]):
    """
    Manager provides table-level operations - like Django's Manager.
    """

    def __init__(self):
        self.model_class: type[M] | None = None
        self.storage: Storage | None = None

    def contribute_to_class(self, model_class: type[M], storage: "Storage") -> None:
        self.model_class = model_class
        self.storage = storage

    def _get_queryset(self) -> QuerySet[M]:
        assert self.model_class is not None
        assert self.storage is not None
        return QuerySet(self.model_class, self.storage)

    def all(self) -> QuerySet[M]:
        return self._get_queryset()

    def filter(self, **kwargs) -> QuerySet[M]:
        return self._get_queryset().filter(**kwargs)

    def exclude(self, **kwargs) -> QuerySet[M]:
        return self._get_queryset().exclude(**kwargs)

    def get(self, **kwargs) -> M:
        """Get single record or raise exception."""
        results = self.filter(**kwargs).all()
        if len(results) == 0:
            raise ValueError("Object not found")
        if len(results) > 1:
            raise ValueError("Multiple objects returned")
        return results[0]

    def create(self, **kwargs) -> M:
        """Create and save a new record."""
        assert self.model_class is not None
        obj = self.model_class(**kwargs)
        obj.save()
        return obj


# Storage (In-memory database)


class Storage:
    """Simple in-memory storage - simulates database."""

    _instance: ClassVar["Storage | None"] = None

    def __new__(cls) -> "Storage":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.tables = {}
            cls._instance.sequences = {}
        return cls._instance

    tables: dict[str, dict[int, Any]]
    sequences: dict[str, int]

    def get_next_id(self, table_name: str) -> int:
        current = self.sequences.get(table_name, 0)
        self.sequences[table_name] = current + 1
        return current + 1

    def insert(self, table_name: str, pk: int, obj: Any) -> None:
        if table_name not in self.tables:
            self.tables[table_name] = {}
        self.tables[table_name][pk] = obj

    def update(self, table_name: str, pk: int, obj: Any) -> None:
        if table_name not in self.tables or pk not in self.tables[table_name]:
            raise ValueError(f"Object with pk={pk} not found")
        self.tables[table_name][pk] = obj

    def delete(self, table_name: str, pk: int) -> None:
        if table_name in self.tables and pk in self.tables[table_name]:
            del self.tables[table_name][pk]

    @classmethod
    def reset(cls) -> None:
        """Reset storage - useful for tests."""
        cls._instance = None


# Model Base Class


class ModelMeta(type):
    """Metaclass that sets up fields and manager."""

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        # Collect fields
        fields: dict[str, Field] = {}
        for key, value in list(namespace.items()):
            if isinstance(value, Field):
                fields[key] = value

        namespace["_fields"] = fields

        # Create class
        cls = super().__new__(mcs, name, bases, namespace)

        # Set up manager if not Model base class
        if name != "Model":
            storage = Storage()
            if "objects" not in namespace:
                manager = Manager()
                manager.contribute_to_class(cls, storage)
                cls.objects = manager
            cls._storage = storage

        return cls


class Model(metaclass=ModelMeta):
    """Base model class - inherit to create your models."""

    _fields: ClassVar[dict[str, Field]]
    _storage: ClassVar[Storage]
    objects: ClassVar[Manager]

    id: int | None = None

    def __init__(self, **kwargs):
        self.id = kwargs.pop("id", None)

        for name, field_obj in self._fields.items():
            value = kwargs.get(name)
            if value is None and field_obj.default is not None:
                value = field_obj.default
            setattr(self, name, field_obj.to_python(value))

    def validate(self) -> None:
        """Validate all fields."""
        errors = []
        for name, field_obj in self._fields.items():
            try:
                field_obj.validate(getattr(self, name))
            except ValueError as e:
                errors.append(str(e))
        if errors:
            raise ValueError(f"Validation errors: {'; '.join(errors)}")

    def save(self) -> None:
        """Save to storage."""
        self.validate()

        # Handle auto timestamps
        for name, field_obj in self._fields.items():
            if isinstance(field_obj, DateTimeField):
                if field_obj.auto_now or (field_obj.auto_now_add and self.id is None):
                    setattr(self, name, datetime.now())

        table_name = self.__class__.__name__.lower()

        if self.id is None:
            self.id = self._storage.get_next_id(table_name)
            self._storage.insert(table_name, self.id, self)
        else:
            self._storage.update(table_name, self.id, self)

    def delete(self) -> None:
        """Delete from storage."""
        if self.id is not None:
            table_name = self.__class__.__name__.lower()
            self._storage.delete(table_name, self.id)
            self.id = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = {"id": self.id}
        for name in self._fields:
            value = getattr(self, name)
            if isinstance(value, datetime):
                value = value.isoformat()
            data[name] = value
        return data

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"


# Example Usage


class Article(Model):
    title = CharField(max_length=200, min_length=1)
    content = CharField(max_length=10000, required=False, default="")
    author = CharField(max_length=100)
    views = IntegerField(default=0, min_value=0)
    is_published = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


def main():
    # Reset storage for clean state
    Storage.reset()

    print("=" * 60)
    print("Creating Articles")
    print("=" * 60)

    # Create articles
    article1 = Article.objects.create(
        title="Introduction to Django",
        content="Django is a Python web framework...",
        author="Alice",
        is_published=True,
    )
    print(f"Created: {article1.to_dict()}")

    article2 = Article.objects.create(
        title="Advanced ORM Techniques",
        content="Learn about QuerySets...",
        author="Bob",
        views=100,
    )
    print(f"Created: {article2.to_dict()}")

    article3 = Article.objects.create(
        title="Django REST Framework",
        content="Building APIs with Django...",
        author="Alice",
        is_published=True,
        views=50,
    )
    print(f"Created: {article3.to_dict()}")

    print("\n" + "=" * 60)
    print("Querying")
    print("=" * 60)

    # All articles
    print(f"\nAll articles count: {Article.objects.all().count()}")

    # Filter by author
    alice_articles = Article.objects.filter(author="Alice").all()
    print(f"\nArticles by Alice: {[a.title for a in alice_articles]}")

    # Filter published
    published = Article.objects.filter(is_published=True).all()
    print(f"Published articles: {[a.title for a in published]}")

    # Chained filters
    alice_published = (
        Article.objects.filter(author="Alice").filter(is_published=True).all()
    )
    print(f"Alice's published: {[a.title for a in alice_published]}")

    # Order by views descending
    by_views = Article.objects.all().order_by("-views").all()
    print(f"By views (desc): {[(a.title, a.views) for a in by_views]}")

    # Get single object
    django_article = Article.objects.get(title="Introduction to Django")
    print(f"\nSingle get: {django_article.title}")

    print("\n" + "=" * 60)
    print("Updating")
    print("=" * 60)

    # Update article
    article1.views = 200
    article1.save()
    print(f"Updated views: {article1.views}")

    print("\n" + "=" * 60)
    print("Deleting")
    print("=" * 60)

    # Delete article
    article2.delete()
    print(f"After delete, count: {Article.objects.all().count()}")

    print("\n" + "=" * 60)
    print("Validation")
    print("=" * 60)

    try:
        bad_article = Article(title="", author="Test")
        bad_article.save()
    except ValueError as e:
        print(f"Validation error: {e}")


if __name__ == "__main__":
    main()
