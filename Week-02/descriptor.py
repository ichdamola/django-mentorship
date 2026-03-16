class Descriptor:
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f"__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        setattr(obj, self.private_name, value)


class ValidatedField(Descriptor):
    def __init__(self, validator=None):
        self.validator = validator

    def __set__(self, obj, value):
        if self.validator:
            self.validator(value)
        super().__set__(obj, value)


class TypedField(Descriptor):
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


class Product:
    name = TypedField(str)
    price = RangeField(min_value=0)
    quantity = RangeField(min_value=0, max_value=10000)

    def __init__(self, name: str, price: float, quantity: int = 0):
        self.name = name
        self.price = price
        self.quantity = quantity


def main():
    laptop = Product("Macbook Pro", 1999.99, 50)
    print(f"Product: {laptop.name}, ${laptop.price}, qty: {laptop.quantity}")

    try:
        laptop.name = 12345
    except TypeError as e:
        print(f"Type error: {e}")

    try:
        laptop.price = -100
    except ValueError as e:
        print(f"Value error: {e}")

    try:
        laptop.quantity = 999999
    except ValueError as e:
        print(f"Value error: {e}")


if __name__ == "__main__":
    main()
