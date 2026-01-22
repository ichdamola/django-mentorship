"""
Simulating how Django's ORM works under the hood
This helps understand what Django does automatically
"""

from datetime import datetime
from typing import Any


class Field:
    """Base class for all field types (like Django's models.field)"""

    def __init__(self, required: bool = True, default: Any = None):
        self.required = required
        self.default = default
        self.name: str | None = None  # Set by ModelMeta

    def validate(self, value: Any) -> None:
        """Validate the value. Override in subclasses"""
        if self.required and value is None and self.default is None:
            raise ValueError(f"{self.name} is required")

    def to_python(self, value: Any) -> Any:
        """Convert value to python type. Override in subclasses"""
        return value


class CharField(Field):
    """String field with max length (like Django's Charfield)"""

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
    """Integer field (like Django's IntegerField)"""

    def validate(self, value: Any) -> None:
        super().validate(value)
        if value is not None and not isinstance(value, int):
            raise ValueError(f"{self.name} must be an integer")

    def to_python(self, value: Any) -> int | None:
        if value is None:
            return self.default
        return int(value)


class DateTimeField(Field):
    """Datetime field with auto_now option (like Django's DateTimeField)"""

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
    Metaclass that collects Field instances from class definition
    This is similar to Django's ModelBase metaclass
    """

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        fields = {}

        # Collect fields from parent classes
        for base in bases:
            # Model creation - bases = (object,) - tuple | base = object
            # Article creation - bases = (Model,) - tuple | base = Model
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
    Base model class (like Django's models.Model)
    All your models inherit from this
    """

    _fields: dict[str, Field] = {}

    def __init__(self, **kwargs):
        # Set field values
        for name, field in self._fields.items():
            value = kwargs.get(name)
            python_value = field.to_python(value)
            setattr(self, name, python_value)

    def validate(self) -> None:
        """Validate all fields"""
        errors = []
        for name, field in self._fields.items():
            try:
                field.validate(getattr(self, name))
            except ValueError as e:
                errors.append(str(e))
        if errors:
            raise ValueError(f"Validation errors: {', '.join(errors)}")

    def save(self) -> None:
        """Simulate saving to database"""
        self.validate()
        print(f"Saving {self.__class__.__name__}: {self.to_dict()}")

    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {name: getattr(self, name) for name in self._fields}

    def __repr__(self) -> str:
        fields_str = ", ".join(
            f"{name}={getattr(self, name)!r}" for name in self._fields
        )
        return f"{self.__class__.__name__}({fields_str})"


# To use like Django
class Article(Model):
    """Example model - just like in Django"""

    title = CharField(max_length=200)
    content = CharField(max_length=10000, required=False, default="")
    views = IntegerField(default=0)
    created_at = DateTimeField(auto_now=True)


def main():
    # create an article
    article = Article(title="Hello World", content="My first article")
    print(f"Created: {article}")

    # Validate and save
    article.save()

    # try invalid data
    try:
        bad_article = Article()  # Missing required title
        bad_article.save()
    except ValueError as e:
        print(f"Validation error: {e}")


if __name__ == "__main__":
    main()


#######################################
# 1. ModelMeta metaclass collect Field instances from class definition and parent class, sets their name attribute and stores them in the _fields dictionary for model class.

# 2. The Field (e.g Charfield) had no idea what name it will be called (e.g title, content, etc). It waits for ModelMeta to collect this information. Since Field objects know their attribute name, it can easily be referenced by name in validations, which is also useful in error messages (e.g. "title exceeds max length").

# 3. Using this instance where Article inherits from Model. The Parent (Model) has class attribute _fields which is empty, which is naturally inherited by the child class (Article), now Article has the _fields. Recall the ModelMeta is the metaclass (class builder) for Model class itself, so from the ModelMeta, it loops through Models and the now included _fields in the Article class, it then updates it by adding the Article's own fields to it.
# In summary Article._fields = {parent fields} + {child fields}. If Model had field, Article would get them too
