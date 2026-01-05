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
            raise ValueError(f"{self.name} exceeds max length of {self.max_length}")

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
    """Metaclass that collects Field instances from class definition. This is similar to Django's ModelBase metaclass."""

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        fields = {}

        # Collect fields from parent classes
        for base in bases:
            if hasattr(base, "_fields"):
                fields.update(base._fields)

        # Collect fields from this class
        for key, value in list(namespace.items()):
            if isinstance(value, Field):
                value.name = key
                fields[key] = value

        namespace["_fields"] = fields
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
            f"{name}={getattr(self, name)!r}" for name in self._fields
        )
        return f"{self.__class__.__name__}({fields_str})"
    
    # 1.) The ModelMeta metaclass runs when a model class is created and finds all Field attributes and collects them into _Fields
    # 2.) Because it doesn't know what it's called untl the class is created
    # 3.) Child models inherit all fields from their parent models and can add or overide them


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
