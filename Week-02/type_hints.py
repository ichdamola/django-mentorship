"""
Type hints - making your code self-documenting and safer.
"""

from dataclasses import dataclass
from typing import Protocol, TypeVar, Generic
from collections.abc import Callable, Iterable
from typing import TypedDict, NotRequired



# Part 1: Basic Type Hints


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


# Part 2: Dataclasses (Used heavily in modern Django)


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


# Part 3: Protocols (Structural Subtyping)


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


# Part 4: Generics (Like Django's QuerySet[Model])

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


# Part 5: TypedDict (For JSON/Dict structures)

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
