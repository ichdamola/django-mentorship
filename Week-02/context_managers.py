"""
Context managers - managing resources safely.
Essential for database transactions in Django.
"""

import time
from contextlib import contextmanager
from typing import Generator

# Part 1: Class-based Context Manager


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


# Part 2: Generator-based Context Manager (using contextlib)


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


# Part 3: Nested Context Managers


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

    with temporary_file("test_file.txt") as f:
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
