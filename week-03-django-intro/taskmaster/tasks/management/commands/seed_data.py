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