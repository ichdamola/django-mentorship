# Week 02: Python Foundations for Django

## 🎯 Learning Objectives

By the end of this week, you will:

- Master Python concepts essential for Django development
- Understand Object-Oriented Programming patterns used in Django
- Work comfortably with decorators and context managers
- Handle files and exceptions properly
- Understand type hints and how Django uses them

## 📚 Required Reading

| Resource                                                                         | Section                          | Time   |
| -------------------------------------------------------------------------------- | -------------------------------- | ------ |
| [Python Tutorial](https://docs.python.org/3/tutorial/)                           | Chapters 9 (Classes), 8 (Errors) | 60 min |
| [Real Python - OOP](https://realpython.com/python3-object-oriented-programming/) | Full article                     | 45 min |
| [Real Python - Decorators](https://realpython.com/primer-on-python-decorators/)  | Full article                     | 30 min |
| [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)                        | Introduction                     | 20 min |

---

## Part 1: Object-Oriented Python

### Why This Matters for Django

Django is built entirely on OOP principles:

```
┌─────────────────────────────────────────────────────────────────┐
│                   Django's Class Hierarchy                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  models.Model          ◄── Your database tables inherit this    │
│       │                                                         │
│       ▼                                                         │
│  class Article(models.Model):                                   │
│      title = models.CharField(...)                              │
│                                                                 │
│  views.View            ◄── Your views inherit this              │
│       │                                                         │
│       ▼                                                         │
│  class ArticleView(View):                                       │
│      def get(self, request): ...                                │
│                                                                 │
│  forms.Form            ◄── Your forms inherit this              │
│       │                                                         │
│       ▼                                                         │
│  class ArticleForm(forms.Form):                                 │
│      title = forms.CharField(...)                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Exercise 2.1: Classes and Inheritance

**Task**: Create a class hierarchy that mirrors how Django models work.

Create `models_simulation.py`:

```python
"""
Simulating how Django's ORM works under the hood.
This helps you understand what Django does automatically.
"""

from datetime import datetime
from typing import Any


class Field:
    """Base class for all field types (like Django's models.Field)."""

    def __init__(self, required: bool = True, default: Any = None):
        self.required = required
        self.default = default
        self.name: str | None = None  # Set by ModelMeta

    def validate(self, value: Any) -> None:
        """Validate the value. Override in subclasses."""
        if self.required and value is None and self.default is None:
            raise ValueError(f"{self.name} is required")

    def to_python(self, value: Any) -> Any:
        """Convert value to Python type. Override in subclasses."""
        return value


class CharField(Field):
    """String field with max length (like Django's CharField)."""

    def __init__(self, max_length: int = 255, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length

    def validate(self, value: Any) -> None:
        super().validate(value)
        if value is not None and len(str(value)) > self.max_length:
            raise ValueError(
                f"{self.name} exceeds max length of {self.max_length}"
            )

    def to_python(self, value: Any) -> str | None:
        if value is None:
            return self.default
        return str(value)


class IntegerField(Field):
    """Integer field (like Django's IntegerField)."""

    def validate(self, value: Any) -> None:
        super().validate(value)
        if value is not None and not isinstance(value, int):
            raise ValueError(f"{self.name} must be an integer")

    def to_python(self, value: Any) -> int | None:
        if value is None:
            return self.default
        return int(value)


class DateTimeField(Field):
    """DateTime field with auto_now option (like Django's DateTimeField)."""

    def __init__(self, auto_now: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.auto_now = auto_now

    def to_python(self, value: Any) -> datetime | None:
        if self.auto_now:
            return datetime.now()
        if value is None:
            return self.default
        if isinstance(value, datetime):
            return value
        # In real Django, this would parse strings too
        return value


class ModelMeta(type):
    """
    Metaclass that collects Field instances from class definition.
    This is similar to Django's ModelBase metaclass.
    """

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        fields = {}

        # Collect fields from parent classes
        for base in bases:
            if hasattr(base, '_fields'):
                fields.update(base._fields)

        # Collect fields from this class
        for key, value in list(namespace.items()):
            if isinstance(value, Field):
                value.name = key
                fields[key] = value

        namespace['_fields'] = fields
        return super().__new__(mcs, name, bases, namespace)


class Model(metaclass=ModelMeta):
    """
    Base model class (like Django's models.Model).
    All your models inherit from this.
    """

    _fields: dict[str, Field] = {}

    def __init__(self, **kwargs):
        # Set field values
        for name, field in self._fields.items():
            value = kwargs.get(name)
            python_value = field.to_python(value)
            setattr(self, name, python_value)

    def validate(self) -> None:
        """Validate all fields."""
        errors = []
        for name, field in self._fields.items():
            try:
                field.validate(getattr(self, name))
            except ValueError as e:
                errors.append(str(e))
        if errors:
            raise ValueError(f"Validation errors: {', '.join(errors)}")

    def save(self) -> None:
        """Simulate saving to database."""
        self.validate()
        print(f"Saving {self.__class__.__name__}: {self.to_dict()}")

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {name: getattr(self, name) for name in self._fields}

    def __repr__(self) -> str:
        fields_str = ", ".join(
            f"{name}={getattr(self, name)!r}"
            for name in self._fields
        )
        return f"{self.__class__.__name__}({fields_str})"


# Now use it like Django!
class Article(Model):
    """Example model - just like you'd define in Django."""
    title = CharField(max_length=200)
    content = CharField(max_length=10000, required=False, default="")
    views = IntegerField(default=0)
    created_at = DateTimeField(auto_now=True)


def main():
    # Create an article
    article = Article(title="Hello World", content="My first article")
    print(f"Created: {article}")

    # Validate and save
    article.save()

    # Try invalid data
    try:
        bad_article = Article()  # Missing required title
        bad_article.save()
    except ValueError as e:
        print(f"Validation error: {e}")


if __name__ == "__main__":
    main()
```

**Run and understand:**

```bash
uv run python models_simulation.py
```

**Questions to answer (write in comments):**

1. What does the `ModelMeta` metaclass do?
2. Why does `Field` have a `name` attribute that gets set later?
3. How does inheritance work with `_fields`?

---

### Exercise 2.2: Properties and Descriptors

**Task**: Understand how Django's model fields actually work (they're descriptors!).

Create `descriptors.py`:

```python
"""
Understanding Python descriptors - the magic behind Django fields.
"""


class Descriptor:
    """
    A descriptor is an object that defines __get__, __set__, or __delete__.
    Django model fields are descriptors.
    """

    def __set_name__(self, owner, name):
        """Called when the descriptor is assigned to a class attribute."""
        self.name = name
        self.private_name = f"__{name}"

    def __get__(self, obj, objtype=None):
        """Called when the attribute is accessed."""
        if obj is None:
            return self
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        """Called when the attribute is set."""
        setattr(obj, self.private_name, value)


class ValidatedField(Descriptor):
    """A field that validates on assignment."""

    def __init__(self, validator=None):
        self.validator = validator

    def __set__(self, obj, value):
        if self.validator:
            self.validator(value)
        super().__set__(obj, value)


class TypedField(Descriptor):
    """A field that enforces type."""

    def __init__(self, expected_type):
        self.expected_type = expected_type

    def __set__(self, obj, value):
        if value is not None and not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        super().__set__(obj, value)


class RangeField(TypedField):
    """Numeric field with min/max validation."""

    def __init__(self, min_value=None, max_value=None):
        super().__init__(expected_type=(int, float))
        self.min_value = min_value
        self.max_value = max_value

    def __set__(self, obj, value):
        if value is not None:
            if self.min_value is not None and value < self.min_value:
                raise ValueError(f"{self.name} must be >= {self.min_value}")
            if self.max_value is not None and value > self.max_value:
                raise ValueError(f"{self.name} must be <= {self.max_value}")
        super().__set__(obj, value)


# Usage example
class Product:
    name = TypedField(str)
    price = RangeField(min_value=0)
    quantity = RangeField(min_value=0, max_value=10000)

    def __init__(self, name: str, price: float, quantity: int = 0):
        self.name = name
        self.price = price
        self.quantity = quantity


def main():
    # Valid product
    laptop = Product("MacBook Pro", 1999.99, 50)
    print(f"Product: {laptop.name}, ${laptop.price}, qty: {laptop.quantity}")

    # Try invalid type
    try:
        laptop.name = 12345  # Should fail - not a string
    except TypeError as e:
        print(f"Type error: {e}")

    # Try invalid range
    try:
        laptop.price = -100  # Should fail - negative price
    except ValueError as e:
        print(f"Value error: {e}")

    # Try exceeding max
    try:
        laptop.quantity = 999999  # Should fail - exceeds max
    except ValueError as e:
        print(f"Value error: {e}")


if __name__ == "__main__":
    main()
```

> 📖 **Documentation**: [Python Descriptor Guide](https://docs.python.org/3/howto/descriptor.html)

---

## Part 2: Decorators

### Why This Matters for Django

Django uses decorators extensively:

```python
@login_required           # Protect views
def my_view(request):
    pass

@permission_required('can_edit')  # Check permissions
def edit_view(request):
    pass

@csrf_exempt              # Disable CSRF for API endpoints
def api_endpoint(request):
    pass

@cached_property          # Cache expensive computations
def expensive_calculation(self):
    pass
```

---

### Exercise 2.3: Understanding Decorators

**Task**: Build decorators from scratch to understand them completely.

Create `decorators.py`:

```python
"""
Understanding decorators - essential for Django development.
"""

import functools
import time
from typing import Callable, Any


# ============================================================
# Part 1: Basic Decorator Pattern
# ============================================================

def simple_decorator(func: Callable) -> Callable:
    """
    A decorator is a function that takes a function and returns a function.

    This is equivalent to:
        @simple_decorator
        def my_func(): ...

    Which is the same as:
        def my_func(): ...
        my_func = simple_decorator(my_func)
    """
    @functools.wraps(func)  # Preserves function metadata
    def wrapper(*args, **kwargs):
        print(f"Before calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"After calling {func.__name__}")
        return result
    return wrapper


@simple_decorator
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


# ============================================================
# Part 2: Decorator with Arguments
# ============================================================

def repeat(times: int) -> Callable:
    """
    Decorator that repeats function execution.

    When a decorator takes arguments, we need three levels:
    1. The outer function takes decorator arguments
    2. The middle function takes the decorated function
    3. The inner function handles the actual call
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


@repeat(times=3)
def say_hello():
    """Say hello once."""
    print("Hello!")


# ============================================================
# Part 3: Practical Decorators (Like Django Uses)
# ============================================================

def timer(func: Callable) -> Callable:
    """Measure function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0) -> Callable:
    """Retry function on exception (like Django's database retry)."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


def require_auth(func: Callable) -> Callable:
    """
    Simulate Django's @login_required decorator.
    In real Django, this checks request.user.is_authenticated.
    """
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request, 'user_authenticated', False):
            return {"error": "Authentication required", "status": 401}
        return func(request, *args, **kwargs)
    return wrapper


def validate_json(*required_fields: str) -> Callable:
    """Validate that JSON body contains required fields."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            body = getattr(request, 'json_body', {})
            missing = [f for f in required_fields if f not in body]
            if missing:
                return {
                    "error": f"Missing required fields: {missing}",
                    "status": 400
                }
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


# ============================================================
# Part 4: Class-based Decorator (Like Django's method_decorator)
# ============================================================

class CacheResult:
    """
    Class-based decorator that caches results.
    Similar to Django's @cached_property.
    """

    def __init__(self, ttl_seconds: int = 60):
        self.ttl = ttl_seconds
        self.cache: dict[str, tuple[Any, float]] = {}

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"

            # Check cache
            if key in self.cache:
                result, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    print(f"Cache hit for {key}")
                    return result

            # Compute and cache
            result = func(*args, **kwargs)
            self.cache[key] = (result, time.time())
            print(f"Cache miss for {key}")
            return result
        return wrapper


# ============================================================
# Usage Examples
# ============================================================

# Simulating a request object like Django's
class Request:
    def __init__(self, authenticated=False, json_body=None):
        self.user_authenticated = authenticated
        self.json_body = json_body or {}


@require_auth
@validate_json("title", "content")
def create_article(request):
    """Create a new article. Requires auth and valid JSON."""
    return {"success": True, "article": request.json_body}


@timer
@CacheResult(ttl_seconds=5)
def expensive_computation(n: int) -> int:
    """Simulate expensive computation."""
    time.sleep(0.1)  # Simulate work
    return n ** 2


def main():
    print("=" * 60)
    print("Basic Decorator")
    print("=" * 60)
    result = greet("Django")
    print(f"Result: {result}\n")

    print("=" * 60)
    print("Repeat Decorator")
    print("=" * 60)
    say_hello()
    print()

    print("=" * 60)
    print("Auth + Validation Decorators (Stacked)")
    print("=" * 60)

    # Unauthenticated request
    req1 = Request(authenticated=False)
    print(f"Unauth request: {create_article(req1)}")

    # Authenticated but missing fields
    req2 = Request(authenticated=True, json_body={"title": "Test"})
    print(f"Missing fields: {create_article(req2)}")

    # Valid request
    req3 = Request(
        authenticated=True,
        json_body={"title": "Test", "content": "Hello World"}
    )
    print(f"Valid request: {create_article(req3)}")
    print()

    print("=" * 60)
    print("Cached Computation")
    print("=" * 60)
    print(f"First call: {expensive_computation(10)}")
    print(f"Second call (cached): {expensive_computation(10)}")
    print(f"Different arg: {expensive_computation(20)}")


if __name__ == "__main__":
    main()
```

---

## Part 3: Context Managers

### Why This Matters for Django

```python
# Django uses context managers for:
with transaction.atomic():      # Database transactions
    Model.objects.create(...)

with connection.cursor() as c:  # Raw SQL
    c.execute("SELECT ...")

# You'll write them for:
with Timer("operation"):        # Performance measurement
    slow_operation()
```

---

### Exercise 2.4: Context Managers

Create `context_managers.py`:

```python
"""
Context managers - managing resources safely.
Essential for database transactions in Django.
"""

import time
from contextlib import contextmanager
from typing import Generator


# ============================================================
# Part 1: Class-based Context Manager
# ============================================================

class Timer:
    """
    Time a block of code.

    Usage:
        with Timer("my operation"):
            # code here
    """

    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time: float = 0
        self.end_time: float = 0

    def __enter__(self) -> "Timer":
        """Called when entering 'with' block."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        Called when exiting 'with' block.

        Args:
            exc_type: Exception type if raised, None otherwise
            exc_val: Exception instance if raised
            exc_tb: Traceback if exception raised

        Returns:
            True to suppress exception, False to propagate
        """
        self.end_time = time.perf_counter()
        elapsed = self.end_time - self.start_time
        print(f"{self.name} took {elapsed:.4f} seconds")
        return False  # Don't suppress exceptions

    @property
    def elapsed(self) -> float:
        return self.end_time - self.start_time


class DatabaseTransaction:
    """
    Simulate Django's transaction.atomic() context manager.
    Demonstrates rollback on exception.
    """

    def __init__(self, connection_name: str = "default"):
        self.connection = connection_name
        self.savepoint_id: int | None = None
        self._committed = False

    def __enter__(self) -> "DatabaseTransaction":
        self.savepoint_id = id(self)  # Simulate savepoint
        print(f"BEGIN TRANSACTION (savepoint {self.savepoint_id})")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:
            print(f"ROLLBACK (exception: {exc_val})")
            return False  # Re-raise the exception

        print("COMMIT")
        self._committed = True
        return False


# ============================================================
# Part 2: Generator-based Context Manager (using contextlib)
# ============================================================

@contextmanager
def timer(name: str = "operation") -> Generator[None, None, None]:
    """
    Same as Timer class, but using @contextmanager decorator.
    This is often simpler for straightforward cases.
    """
    start = time.perf_counter()
    try:
        yield  # Code in 'with' block runs here
    finally:
        end = time.perf_counter()
        print(f"{name} took {end - start:.4f} seconds")


@contextmanager
def temporary_file(filename: str) -> Generator[str, None, None]:
    """
    Create a temporary file that's cleaned up automatically.
    """
    import os

    print(f"Creating temporary file: {filename}")
    # Create empty file
    with open(filename, "w") as f:
        f.write("")

    try:
        yield filename
    finally:
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Cleaned up: {filename}")


@contextmanager
def suppress_exceptions(*exception_types):
    """
    Suppress specific exception types (like contextlib.suppress).
    """
    try:
        yield
    except exception_types as e:
        print(f"Suppressed: {type(e).__name__}: {e}")


# ============================================================
# Part 3: Nested Context Managers
# ============================================================

@contextmanager
def log_block(name: str):
    """Log entry and exit of a code block."""
    print(f">>> Entering {name}")
    try:
        yield
    finally:
        print(f"<<< Exiting {name}")


def main():
    print("=" * 60)
    print("Class-based Context Manager")
    print("=" * 60)

    with Timer("sleep operation") as t:
        time.sleep(0.1)
    print(f"Recorded elapsed time: {t.elapsed:.4f}s\n")

    print("=" * 60)
    print("Database Transaction Simulation")
    print("=" * 60)

    # Successful transaction
    print("Successful transaction:")
    with DatabaseTransaction() as txn:
        print("  Inserting record...")
        print("  Updating record...")

    # Failed transaction
    print("\nFailed transaction:")
    try:
        with DatabaseTransaction() as txn:
            print("  Inserting record...")
            raise ValueError("Something went wrong!")
    except ValueError:
        print("  Exception was re-raised as expected\n")

    print("=" * 60)
    print("Generator-based Context Manager")
    print("=" * 60)

    with timer("computation"):
        sum(range(1000000))
    print()

    print("=" * 60)
    print("Temporary File Management")
    print("=" * 60)

    with temporary_file("/tmp/test_file.txt") as f:
        with open(f, "w") as file:
            file.write("Hello, World!")
        print(f"File exists: {f}")
    print()

    print("=" * 60)
    print("Nested Context Managers")
    print("=" * 60)

    with log_block("outer"):
        with log_block("inner"):
            print("Doing work...")


if __name__ == "__main__":
    main()
```

---

## Part 4: Type Hints

### Why This Matters for Django

Modern Django uses type hints extensively. They help with:

- IDE autocompletion
- Bug prevention
- Documentation
- Tooling (mypy, pyright)

```python
# Django example with type hints
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet

def get_articles(request: HttpRequest) -> HttpResponse:
    articles: QuerySet[Article] = Article.objects.all()
    return render(request, "articles.html", {"articles": articles})
```

---

### Exercise 2.5: Type Hints

Create `type_hints.py`:

```python
"""
Type hints - making your code self-documenting and safer.
"""

from dataclasses import dataclass
from typing import Any, Protocol, TypeVar, Generic
from collections.abc import Callable, Iterable


# ============================================================
# Part 1: Basic Type Hints
# ============================================================

def greet(name: str) -> str:
    """Type hints for simple function."""
    return f"Hello, {name}!"


def process_items(items: list[str], transform: Callable[[str], str]) -> list[str]:
    """
    Type hints with generics and callables.

    Args:
        items: List of strings to process
        transform: Function that takes and returns a string
    """
    return [transform(item) for item in items]


def find_item(items: list[str], predicate: Callable[[str], bool]) -> str | None:
    """Union type for optional return."""
    for item in items:
        if predicate(item):
            return item
    return None


# ============================================================
# Part 2: Dataclasses (Used heavily in modern Django)
# ============================================================

@dataclass
class User:
    """
    Dataclass - cleaner than __init__ boilerplate.
    Django's forms and serializers use similar patterns.
    """
    id: int
    username: str
    email: str
    is_active: bool = True

    def full_display(self) -> str:
        status = "active" if self.is_active else "inactive"
        return f"{self.username} ({self.email}) - {status}"


@dataclass(frozen=True)
class Config:
    """Immutable configuration object."""
    database_url: str
    debug: bool
    secret_key: str


# ============================================================
# Part 3: Protocols (Structural Subtyping)
# ============================================================

class Renderable(Protocol):
    """
    Protocol defines expected interface without inheritance.
    Like Django's duck typing - if it has render(), it's renderable.
    """
    def render(self) -> str: ...


class HTMLComponent:
    """Implements Renderable protocol."""
    def __init__(self, tag: str, content: str):
        self.tag = tag
        self.content = content

    def render(self) -> str:
        return f"<{self.tag}>{self.content}</{self.tag}>"


class TextComponent:
    """Also implements Renderable protocol."""
    def __init__(self, text: str):
        self.text = text

    def render(self) -> str:
        return self.text


def render_all(components: Iterable[Renderable]) -> str:
    """Works with any object that has render() method."""
    return "\n".join(c.render() for c in components)


# ============================================================
# Part 4: Generics (Like Django's QuerySet[Model])
# ============================================================

T = TypeVar("T")


class Repository(Generic[T]):
    """
    Generic repository pattern.
    Similar to how Django's Manager works with model types.
    """

    def __init__(self):
        self._items: dict[int, T] = {}
        self._next_id: int = 1

    def add(self, item: T) -> int:
        item_id = self._next_id
        self._items[item_id] = item
        self._next_id += 1
        return item_id

    def get(self, item_id: int) -> T | None:
        return self._items.get(item_id)

    def all(self) -> list[T]:
        return list(self._items.values())

    def filter(self, predicate: Callable[[T], bool]) -> list[T]:
        return [item for item in self._items.values() if predicate(item)]


# ============================================================
# Part 5: TypedDict (For JSON/Dict structures)
# ============================================================

from typing import TypedDict, NotRequired


class ArticleDict(TypedDict):
    """
    Type-safe dictionary structure.
    Useful for API responses, JSON data.
    """
    id: int
    title: str
    content: str
    author: str
    published: NotRequired[bool]  # Optional field


def process_article(article: ArticleDict) -> str:
    """Type checker knows exact structure of article dict."""
    return f"{article['title']} by {article['author']}"


def main():
    print("=" * 60)
    print("Basic Type Hints")
    print("=" * 60)

    print(greet("Django"))

    items = ["hello", "world"]
    result = process_items(items, str.upper)
    print(f"Processed: {result}")

    found = find_item(items, lambda x: x.startswith("w"))
    print(f"Found: {found}\n")

    print("=" * 60)
    print("Dataclasses")
    print("=" * 60)

    user = User(id=1, username="john", email="john@example.com")
    print(f"User: {user}")
    print(f"Display: {user.full_display()}\n")

    print("=" * 60)
    print("Protocols")
    print("=" * 60)

    components: list[Renderable] = [
        HTMLComponent("h1", "Hello"),
        HTMLComponent("p", "World"),
        TextComponent("Plain text"),
    ]
    print(render_all(components))
    print()

    print("=" * 60)
    print("Generic Repository")
    print("=" * 60)

    # Repository of Users
    user_repo: Repository[User] = Repository()
    user_repo.add(User(1, "alice", "alice@example.com"))
    user_repo.add(User(2, "bob", "bob@example.com", is_active=False))

    print(f"All users: {user_repo.all()}")
    print(f"Active users: {user_repo.filter(lambda u: u.is_active)}\n")

    print("=" * 60)
    print("TypedDict")
    print("=" * 60)

    article: ArticleDict = {
        "id": 1,
        "title": "Type Hints in Python",
        "content": "Type hints make code safer...",
        "author": "Jane Doe",
    }
    print(process_article(article))


if __name__ == "__main__":
    main()
```

---

## 📝 Weekly Project: Mini ORM

**Task**: Build a simplified ORM that demonstrates the patterns Django uses.

Create `mini_orm.py`:

```python
"""
Mini ORM Project - Understanding Django's internals.

Build a simplified ORM that supports:
1. Model definition with typed fields
2. Validation
3. CRUD operations (in-memory)
4. Simple querying with filtering
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypeVar, Generic, Callable, ClassVar
from abc import ABC, abstractmethod


# Type variable for generic model operations
M = TypeVar("M", bound="Model")


# ============================================================
# Fields
# ============================================================

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
                raise ValueError(
                    f"{self.name}: Max length is {self.max_length}"
                )
            if len(value) < self.min_length:
                raise ValueError(
                    f"{self.name}: Min length is {self.min_length}"
                )


class IntegerField(Field):
    def __init__(self, min_value: int | None = None, max_value: int | None = None, **kwargs):
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


# ============================================================
# QuerySet
# ============================================================

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
            qs._filters.append(
                lambda obj, f=field_name, v=value: getattr(obj, f) == v
            )
        return qs

    def exclude(self, **kwargs) -> "QuerySet[M]":
        """Exclude by field values."""
        qs = self._clone()
        for field_name, value in kwargs.items():
            qs._filters.append(
                lambda obj, f=field_name, v=value: getattr(obj, f) != v
            )
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
            results = results[:self._limit]

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


# ============================================================
# Manager
# ============================================================

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


# ============================================================
# Storage (In-memory database)
# ============================================================

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


# ============================================================
# Model Base Class
# ============================================================

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


# ============================================================
# Example Usage
# ============================================================

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
        Article.objects
        .filter(author="Alice")
        .filter(is_published=True)
        .all()
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
```

**Run your Mini ORM:**

```bash
uv run python mini_orm.py
```

---

## 📋 Submission Checklist

Before moving to Week 03, ensure:

- [ ] Completed all exercises (models_simulation.py, descriptors.py, decorators.py, context_managers.py, type_hints.py)
- [ ] Built and tested mini_orm.py
- [ ] All code passes `uv run ruff check .`
- [ ] All code is formatted with `uv run ruff format .`
- [ ] Can explain: classes, inheritance, decorators, context managers, type hints
- [ ] Understand how these patterns appear in Django

---

## 🔗 Additional Resources

- [Python Data Model](https://docs.python.org/3/reference/datamodel.html)
- [Fluent Python (Book)](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [mypy Documentation](https://mypy.readthedocs.io/)

---

**Next**: [Week 03: Django Introduction →](../week-03-django-intro/README.md)
