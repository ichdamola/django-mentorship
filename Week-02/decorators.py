import functools
import time
from typing import Callable, Any

# Part 1: Basic Decorator Pattern


def simple_decorator(func: Callable) -> Callable:
    """A decorator is a function that takes a function and returns a function.
    This is equivalent to:
    @simple_decorator
    def my_func(): ...

    Which is the same as:
    def my func(): ...
    my_func = simple_decorator(my_func)
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Before calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"After calling {func.__name__}")
        return result

    return wrapper


@simple_decorator
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"hello, {name}!"


# Part 2: Decorator with Arguements


def repeat(times: int) -> Callable:
    """Decorator that repeats function execution.

    When a decorator takes arguements, we need three levels
    1. The outer function takes decorator arguements
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


# Part 3: Practical Decorators (Like Django Uses)


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
        if not getattr(request, "user_authenticated", False):
            return {"error": "Authentication required", "status": 401}
        return func(request, *args, **kwargs)

    return wrapper


def validate_json(*required_fields: str) -> Callable:
    """Validate that JSON body contains required fields."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            body = getattr(request, "json_body", {})
            missing = [f for f in required_fields if f not in body]
            if missing:
                return {"error": f"Missing required fields: {missing}", "status": 400}
            return func(request, *args, **kwargs)

        return wrapper

    return decorator


# Part 4: Class-based Decorator (Like Django's method_decorator)


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


# Usage Examples

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
    return n**2


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
        authenticated=True, json_body={"title": "Test", "content": "Hello World"}
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
