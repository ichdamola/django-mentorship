"""
TaskMaster Models

Models define the structure of your database tables.
Each model class maps to a database table.
Each attribute maps to a database column.
"""

from django.db import models
from django.utils import timezone


class Category(models.Model):
    """
    Categories for organizing tasks.

    Database table: tasks_category
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., 'Work', 'Personal')",
    )
    description = models.TextField(
        blank=True, default="", help_text="Optional description"
    )
    color = models.CharField(
        max_length=7, default="#6c757d", help_text="Hex colour code (e.g., '#ff5733')"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        """String representation shown in admin and shell"""
        return self.name


class Priority(models.IntegerChoices):
    """Enum for task priorities unsing IntegerChoices."""

    LOW = 1, "Low"
    MEDIUM = 2, "Medium"
    HIGH = 3, "High"
    URGENT = 4, "Urgent"


class Status(models.TextChoices):
    """Enum for task status using TextChoices"""

    PENDING = "pending", "Pending"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Task(models.Model):
    """
    A task in the task management system

    Database table: tasks_task
    """

    # Required fields
    title = models.CharField(max_length=200, help_text="Task title")

    # Optional fields
    description = models.TextField(
        blank=True, default="", help_text="Detailed task description"
    )

    # Choice field with enums
    priority = models.IntegerField(
        choices=Priority.choices,
        default=Priority.MEDIUM,
        help_text="Task priority level",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Current task status",
    )

    # Date fields
    due_date = models.DateField(null=True, blank=True, help_text="Optional due date")

    # Timestampes (auto-managed)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Relationship: Many tasks can belong to one category
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,  # if category is deleted, set to NULL
        null=True,
        blank=True,
        related_name="tasks",  # category.tasks.all()
        help_text="Task category",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self) -> str:
        return self.title

    def mark_completed(self) -> None:
        """Mark the task as completed"""
        self.status = Status.COMPLETED
        self.completed_at = timezone.now()
        self.save()

    @property
    def is_overdue(self) -> bool:
        """Check if task is past due"""
        if self.due_date and self.status != Status.COMPLETED:
            return self.due_date < timezone.now().date()
        return False

    @property
    def priority_display(self) -> str:
        """Get human-readable priority"""
        return Priority(self.priority).label


class Tag(models.Model):
    """
    Tags for flexible task categorization.
    Many-to-many relationship with Task
    """

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Add many-to-many field to Task (can also be defined inline)
Task.add_to_class(
    "tags",
    models.ManyToManyField(
        Tag, blank=True, related_name="tasks", help_text="Tags for this task"
    ),
)
