# Week 04: Models Basics - Django ORM

## 🎯 Learning Objectives

By the end of this week, you will:

- Understand Django's ORM and how it maps Python classes to database tables
- Create models with various field types
- Use migrations to manage database schema changes
- Perform basic CRUD operations using the ORM
- Understand relationships between models

## 📚 Required Reading

| Resource                                                                   | Section         | Time   |
| -------------------------------------------------------------------------- | --------------- | ------ |
| [Django Models](https://docs.djangoproject.com/en/5.0/topics/db/models/)   | Full page       | 45 min |
| [Field Types](https://docs.djangoproject.com/en/5.0/ref/models/fields/)    | All field types | 30 min |
| [Making Queries](https://docs.djangoproject.com/en/5.0/topics/db/queries/) | Full page       | 45 min |
| [Migrations](https://docs.djangoproject.com/en/5.0/topics/migrations/)     | Overview        | 20 min |

---

## Part 1: Understanding the ORM

### What is an ORM?

```
┌─────────────────────────────────────────────────────────────────┐
│                Object-Relational Mapping (ORM)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Python Code                        SQL / Database              │
│   ────────────                       ─────────────               │
│                                                                  │
│   class Task(models.Model):    ──►   CREATE TABLE tasks (       │
│       title = CharField(100)              id BIGINT PRIMARY KEY, │
│       done = BooleanField()               title VARCHAR(100),    │
│                                           done BOOLEAN           │
│                                      );                          │
│                                                                  │
│   Task.objects.create(         ──►   INSERT INTO tasks          │
│       title="Learn ORM"                   (title, done)          │
│   )                                  VALUES ('Learn ORM', false);│
│                                                                  │
│   Task.objects.filter(         ──►   SELECT * FROM tasks        │
│       done=True                      WHERE done = true;          │
│   )                                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Benefits:**

- Write Python, not SQL
- Database-agnostic (switch between SQLite, PostgreSQL, MySQL)
- Automatic schema migrations
- Protection against SQL injection
- Pythonic query syntax

---

## Part 2: Creating Models

### Exercise 4.1: Define Your First Models

Continue with your TaskMaster project from Week 03. Edit `tasks/models.py`:

```python
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
        help_text="Category name (e.g., 'Work', 'Personal')"
    )
    description = models.TextField(
        blank=True,  # Can be empty in forms
        default="",  # Default value in database
        help_text="Optional description"
    )
    color = models.CharField(
        max_length=7,
        default="#6c757d",
        help_text="Hex color code (e.g., '#ff5733')"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"  # Correct plural form
        ordering = ["name"]  # Default ordering

    def __str__(self) -> str:
        """String representation shown in admin and shell."""
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
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Task(models.Model):
    """
    A task in the task management system.

    Database table: tasks_task
    """
    # Required fields
    title = models.CharField(
        max_length=200,
        help_text="Task title"
    )

    # Optional fields
    description = models.TextField(
        blank=True,
        default="",
        help_text="Detailed task description"
    )

    # Choice fields with enums
    priority = models.IntegerField(
        choices=Priority.choices,
        default=Priority.MEDIUM,
        help_text="Task priority level"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Current task status"
    )

    # Date fields
    due_date = models.DateField(
        null=True,  # Can be NULL in database
        blank=True,  # Can be empty in forms
        help_text="Optional due date"
    )

    # Timestamps (auto-managed)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Relationship: Many tasks can belong to one category
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,  # If category deleted, set to NULL
        null=True,
        blank=True,
        related_name="tasks",  # category.tasks.all()
        help_text="Task category"
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
    """
    Tags for flexible task categorization.
    Many-to-many relationship with Task.
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name


# Add many-to-many field to Task (can also be defined inline)
Task.add_to_class(
    'tags',
    models.ManyToManyField(
        Tag,
        blank=True,
        related_name="tasks",
        help_text="Tags for this task"
    )
)
```

---

### Exercise 4.2: Understanding Field Types

```
┌─────────────────────────────────────────────────────────────────┐
│                    Common Django Field Types                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TEXT FIELDS                                                     │
│  ├── CharField(max_length=N)    VARCHAR(N) - short text         │
│  ├── TextField()                 TEXT - long text                │
│  ├── EmailField()                VARCHAR with email validation   │
│  ├── URLField()                  VARCHAR with URL validation     │
│  └── SlugField()                 VARCHAR for URL-safe strings    │
│                                                                  │
│  NUMBER FIELDS                                                   │
│  ├── IntegerField()              INTEGER                         │
│  ├── BigIntegerField()           BIGINT                          │
│  ├── FloatField()                FLOAT                           │
│  ├── DecimalField(max_digits, decimal_places)  DECIMAL          │
│  └── PositiveIntegerField()      Unsigned INTEGER                │
│                                                                  │
│  BOOLEAN FIELDS                                                  │
│  ├── BooleanField()              BOOLEAN (required)              │
│  └── NullBooleanField()          BOOLEAN (nullable) - deprecated │
│                                                                  │
│  DATE/TIME FIELDS                                                │
│  ├── DateField()                 DATE                            │
│  ├── TimeField()                 TIME                            │
│  ├── DateTimeField()             DATETIME/TIMESTAMP              │
│  └── DurationField()             INTERVAL                        │
│                                                                  │
│  RELATIONSHIP FIELDS                                             │
│  ├── ForeignKey()                Many-to-one                     │
│  ├── OneToOneField()             One-to-one                      │
│  └── ManyToManyField()           Many-to-many                    │
│                                                                  │
│  OTHER FIELDS                                                    │
│  ├── FileField()                 File upload                     │
│  ├── ImageField()                Image upload                    │
│  ├── JSONField()                 JSON data                       │
│  └── UUIDField()                 UUID                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Common Field Options:**

| Option               | Description              |
| -------------------- | ------------------------ |
| `null=True`          | Allow NULL in database   |
| `blank=True`         | Allow empty in forms     |
| `default=value`      | Default value            |
| `choices=list`       | Limit to specific values |
| `unique=True`        | Must be unique           |
| `db_index=True`      | Create database index    |
| `help_text="..."`    | Help text for forms      |
| `verbose_name="..."` | Human-readable name      |

> 📖 **Documentation**: [Model Field Reference](https://docs.djangoproject.com/en/5.0/ref/models/fields/)

---

## Part 3: Migrations

### Exercise 4.3: Create and Apply Migrations

```bash
# Create migrations based on model changes
uv run python manage.py makemigrations tasks

# View the generated migration
uv run python manage.py showmigrations

# See the SQL that will be executed
uv run python manage.py sqlmigrate tasks 0001

# Apply migrations
uv run python manage.py migrate
```

**Understanding Migration Files:**

```python
# tasks/migrations/0001_initial.py (auto-generated)
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []  # No dependencies for initial migration

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                # ... more fields
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                # ... fields
            ],
        ),
    ]
```

**Migration Commands:**

| Command                                | Description                          |
| -------------------------------------- | ------------------------------------ |
| `makemigrations`                       | Create migrations from model changes |
| `migrate`                              | Apply migrations to database         |
| `showmigrations`                       | List all migrations and their status |
| `sqlmigrate app_name migration_number` | Show SQL for a migration             |
| `migrate app_name migration_number`    | Migrate to a specific migration      |
| `migrate app_name zero`                | Unapply all migrations for an app    |

---

## Part 4: CRUD Operations

### Exercise 4.4: Create, Read, Update, Delete

Start the Django shell:

```bash
uv run python manage.py shell
```

**CREATE:**

```python
from tasks.models import Category, Task, Tag, Priority, Status

# Method 1: Create and save in one step
category = Category.objects.create(
    name="Work",
    description="Work-related tasks",
    color="#0066cc"
)

# Method 2: Instantiate then save
personal = Category(name="Personal", color="#28a745")
personal.save()

# Create tasks
task1 = Task.objects.create(
    title="Learn Django ORM",
    description="Study models and queries",
    priority=Priority.HIGH,
    category=category
)

task2 = Task.objects.create(
    title="Build TaskMaster",
    priority=Priority.MEDIUM,
    status=Status.IN_PROGRESS,
    category=category
)

# Create tags
urgent = Tag.objects.create(name="urgent")
learning = Tag.objects.create(name="learning")

# Add tags to task (many-to-many)
task1.tags.add(urgent, learning)
```

**READ:**

```python
# Get all tasks
all_tasks = Task.objects.all()
print(f"Total tasks: {all_tasks.count()}")

# Get by primary key
task = Task.objects.get(pk=1)
task = Task.objects.get(id=1)  # Same as above

# Filter (returns QuerySet)
high_priority = Task.objects.filter(priority=Priority.HIGH)
pending = Task.objects.filter(status=Status.PENDING)

# Chained filters (AND)
urgent_pending = Task.objects.filter(
    priority=Priority.HIGH,
    status=Status.PENDING
)

# Exclude
not_completed = Task.objects.exclude(status=Status.COMPLETED)

# Get first/last
first_task = Task.objects.first()
last_task = Task.objects.last()

# Order by
by_priority = Task.objects.order_by('-priority')  # Descending
by_date = Task.objects.order_by('created_at')  # Ascending

# Field lookups
contains = Task.objects.filter(title__icontains="django")  # Case-insensitive
starts = Task.objects.filter(title__startswith="Learn")
gt = Task.objects.filter(priority__gt=2)  # Greater than
gte = Task.objects.filter(priority__gte=2)  # Greater than or equal
in_list = Task.objects.filter(status__in=[Status.PENDING, Status.IN_PROGRESS])

# Related objects
work_category = Category.objects.get(name="Work")
work_tasks = work_category.tasks.all()  # Using related_name

# Get with related (optimized queries)
tasks_with_category = Task.objects.select_related('category').all()
```

**UPDATE:**

```python
# Update single object
task = Task.objects.get(pk=1)
task.title = "Updated title"
task.save()

# Update multiple objects at once
Task.objects.filter(status=Status.PENDING).update(priority=Priority.LOW)

# Use model method
task.mark_complete()
```

**DELETE:**

```python
# Delete single object
task = Task.objects.get(pk=1)
task.delete()

# Delete multiple objects
Task.objects.filter(status=Status.CANCELLED).delete()

# Be careful with .all()!
# Task.objects.all().delete()  # Deletes everything!
```

---

### Exercise 4.5: QuerySet Methods

```python
from django.db.models import Count, Avg, Sum, Max, Min, Q, F

# Aggregation
from tasks.models import Task, Priority, Status

# Count tasks by status
stats = Task.objects.aggregate(
    total=Count('id'),
    completed=Count('id', filter=Q(status=Status.COMPLETED)),
)
print(stats)  # {'total': 10, 'completed': 3}

# Average priority
avg_priority = Task.objects.aggregate(avg=Avg('priority'))

# Group by with annotation
by_category = Category.objects.annotate(
    task_count=Count('tasks')
).values('name', 'task_count')

by_status = Task.objects.values('status').annotate(
    count=Count('id')
).order_by('status')

# Q objects for complex queries (OR)
complex_query = Task.objects.filter(
    Q(priority=Priority.HIGH) | Q(status=Status.IN_PROGRESS)
)

# F objects for field references
# Get tasks where updated_at > created_at
modified = Task.objects.filter(updated_at__gt=F('created_at'))

# Increase all priorities by 1
Task.objects.update(priority=F('priority') + 1)

# Exists check (more efficient than count)
has_urgent = Task.objects.filter(priority=Priority.URGENT).exists()

# Values and values_list
titles = Task.objects.values_list('title', flat=True)
task_data = Task.objects.values('title', 'status', 'priority')

# Distinct
unique_statuses = Task.objects.values_list('status', flat=True).distinct()

# Slicing (LIMIT)
first_five = Task.objects.all()[:5]
page_two = Task.objects.all()[5:10]
```

---

## Part 5: Relationships Deep Dive

### Exercise 4.6: Understanding Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                    Model Relationships                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ONE-TO-MANY (ForeignKey)                                       │
│  ─────────────────────────                                       │
│  Category ──────< Task                                           │
│  (one)           (many)                                          │
│                                                                  │
│  category = models.ForeignKey(Category, on_delete=models.CASCADE)│
│                                                                  │
│  Usage:                                                          │
│  task.category          # Get category of task                  │
│  category.tasks.all()   # Get all tasks in category             │
│                                                                  │
│  ───────────────────────────────────────────────────────────    │
│                                                                  │
│  MANY-TO-MANY (ManyToManyField)                                 │
│  ─────────────────────────────                                   │
│  Task >──────< Tag                                               │
│  (many)       (many)                                             │
│                                                                  │
│  tags = models.ManyToManyField(Tag)                             │
│                                                                  │
│  Usage:                                                          │
│  task.tags.all()        # Get all tags for task                 │
│  task.tags.add(tag)     # Add tag to task                       │
│  task.tags.remove(tag)  # Remove tag from task                  │
│  tag.tasks.all()        # Get all tasks with tag                │
│                                                                  │
│  ───────────────────────────────────────────────────────────    │
│                                                                  │
│  ONE-TO-ONE (OneToOneField)                                     │
│  ─────────────────────────                                       │
│  User ──────── Profile                                           │
│  (one)         (one)                                             │
│                                                                  │
│  user = models.OneToOneField(User, on_delete=models.CASCADE)    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**on_delete Options:**

| Option        | Behavior                               |
| ------------- | -------------------------------------- |
| `CASCADE`     | Delete related objects                 |
| `PROTECT`     | Prevent deletion                       |
| `SET_NULL`    | Set to NULL (requires `null=True`)     |
| `SET_DEFAULT` | Set to default value                   |
| `SET(value)`  | Set to specific value                  |
| `DO_NOTHING`  | Do nothing (may cause integrity error) |

---

## 📝 Weekly Project: TaskMaster ORM Operations

Create `tasks/management/commands/seed_data.py`:

```python
"""
Custom management command to seed the database with sample data.
Usage: uv run python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from tasks.models import Category, Task, Tag, Priority, Status


class Command(BaseCommand):
    help = "Seed database with sample data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # Clear existing data
        Task.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()

        # Create categories
        categories = [
            Category.objects.create(name="Work", color="#0066cc", description="Work tasks"),
            Category.objects.create(name="Personal", color="#28a745", description="Personal tasks"),
            Category.objects.create(name="Learning", color="#6f42c1", description="Learning goals"),
            Category.objects.create(name="Health", color="#dc3545", description="Health & fitness"),
        ]
        self.stdout.write(f"Created {len(categories)} categories")

        # Create tags
        tag_names = ["urgent", "important", "quick-win", "blocked", "review", "meeting"]
        tags = [Tag.objects.create(name=name) for name in tag_names]
        self.stdout.write(f"Created {len(tags)} tags")

        # Create tasks
        task_templates = [
            ("Complete quarterly report", "Work", Priority.HIGH),
            ("Review pull requests", "Work", Priority.MEDIUM),
            ("Update documentation", "Work", Priority.LOW),
            ("Team standup meeting", "Work", Priority.MEDIUM),
            ("Buy groceries", "Personal", Priority.MEDIUM),
            ("Call mom", "Personal", Priority.LOW),
            ("Pay bills", "Personal", Priority.HIGH),
            ("Study Django ORM", "Learning", Priority.HIGH),
            ("Read Python book", "Learning", Priority.MEDIUM),
            ("Complete online course", "Learning", Priority.MEDIUM),
            ("Morning workout", "Health", Priority.HIGH),
            ("Meal prep for week", "Health", Priority.MEDIUM),
            ("Schedule doctor appointment", "Health", Priority.LOW),
        ]

        tasks_created = []
        for title, cat_name, priority in task_templates:
            category = next(c for c in categories if c.name == cat_name)
            status = random.choice(list(Status))

            # Random due date within next 14 days or None
            due_date = None
            if random.random() > 0.3:
                due_date = timezone.now().date() + timedelta(days=random.randint(-3, 14))

            task = Task.objects.create(
                title=title,
                description=f"Description for: {title}",
                priority=priority,
                status=status,
                category=category,
                due_date=due_date,
            )

            # Add random tags
            random_tags = random.sample(tags, k=random.randint(0, 3))
            task.tags.add(*random_tags)

            tasks_created.append(task)

        self.stdout.write(f"Created {len(tasks_created)} tasks")
        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
```

Create the management command directory structure:

```bash
mkdir -p tasks/management/commands
touch tasks/management/__init__.py
touch tasks/management/commands/__init__.py
```

Run the seed command:

```bash
uv run python manage.py seed_data
```

Now update your views to use real data from the database!

---

## 📋 Submission Checklist

- [ ] Models created: Category, Task, Tag
- [ ] Migrations created and applied
- [ ] Seed command works
- [ ] Can perform CRUD operations in shell
- [ ] Understand relationships (ForeignKey, ManyToMany)
- [ ] Can use filters, annotations, and aggregations
- [ ] Views updated to use database data

---

**Next**: [Week 05: Views & URLs →](../week-05-views-urls/README.md)
