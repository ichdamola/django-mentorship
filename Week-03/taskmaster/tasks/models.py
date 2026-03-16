from django.db import models
from django.utils import timezone
from django.conf import settings

class Category(models.Model):
    """Categories for organizing tasks. Database table: tasks_category"""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., 'Work', 'Personal')",
    )

    description = models.TextField(
        blank=True,  # Can be empty in forms
        default="",  # Default value in databse
        help_text="Optional description",
    )

    color = models.CharField(
        max_length=7, default="#6c757d", help_text="Hex color code (e.g., '#ff5733')"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"  # Correct plural form
        ordering = ["name"]  # Default ordering

    def __str__(self) -> str:
        """String representation shown in admin and shell"""
        return self.name


class Priority(models.IntegerChoices):
    """Enum for task priorities using IntegerChoices."""

    LOW = 1, "Low"
    MEDIUM = 2, "Medium"
    HIGH = 3, "High"
    URGENT = 4, "Urgent"


class Status(models.TextChoices):
    """Enum for task status using TextChoices."""

    PENDING = "pending", "Pending"
    IN_PROGRESS = "in_progress", "In progress"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Task(models.Model):
    """A task in the task management system. Database table: tasks_task"""
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')

    # Required fields
    title = models.CharField(max_length=200, help_text="Task title")

    # Optional fields
    description = models.TextField(
        blank=True, default="", help_text="Detained task description"
    )

    # Choice fields with enums
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
    due_date = models.DateField(
        null=True,  # Can be NULL in database
        blank=True,  # Can be empty in forms
        help_text="Optional due date",
    )

    # Timestamps ( auto-managed)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Relationship: Many tasks can be belong to one category
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,  # If category deleted, set to NULL
        null=True,
        blank=True,
        related_name="tasks",  # category.tasks.all()
        help_text="Task category",
    )

    class Meta:
        ordering = ["-created_at"]  # Newest first
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self) -> str:
        return self.title

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.status = Status.COMPLETED
        self.completed_at = timezone.now()
        self.save()

    @property
    def is_overdue(self) -> bool:
        """Check if task is past due date."""
        if self.due_date and self.status != Status.COMPLETED:
            return self.due_date < timezone.now().date()
        return False

    @property
    def priority_display(self) -> str:
        """Get human-readable priority."""
        return Priority(self.priority).label


class Tag(models.Model):
    """Tags for flexible task categorization. Many-to-many relationship with Task."""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name


# Add many-to-many field to Task (can also be defined inline)
Task.add_to_class(
    "tags",
    models.ManyToManyField(
        Tag, blank=True, related_name="tasks", help_text="Tags for this task"
    ),
)


