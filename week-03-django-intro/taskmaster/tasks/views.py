from django.http import HttpRequest, HttpResponse
from django.db.models import Count, Q, Avg
from .models import Task, Status


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<h1>TaskMaster</h1><p>Welcome to your task manager!</p>")


def task_list(request: HttpRequest) -> HttpResponse:
    tasks = Task.objects.select_related("category").all()

    html = "<h1>Tasks</h1><ul>"
    for task in tasks:
        category_name = task.category.name if task.category else "No Category"
        html += f"<li><a href='/tasks/{task.id}/'>{task.title}</a> - {task.status} - {category_name}</li>"
    html += "</ul>"

    return HttpResponse(html)


def task_detail(request: HttpRequest, task_id: int) -> HttpResponse:
    task = Task.objects.select_related("category").get(id=task_id)
    category_name = task.category.name if task.category else "No Category"

    html = f""""
    <h1>Task #{task.id}</h1>
    <p>Title: {task.title}</p>
    <p>Status: {task.status}</p>
    <p>Priority: {task.priority_display}</p>
    <p>Category: {category_name}</p>
    <p>Description: {task.description}</p>
    """

    return HttpResponse(html)


def about(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<h1>About Page</h1>")


def stats(request: HttpRequest) -> HttpResponse:
    summary = Task.objects.aggregate(
        total_tasks=Count("id"),
        completed_tasks=Count("id", filter=Q(status=Status.COMPLETED)),
        average_priority=Avg("priority"),
    )

    html = f"""
    <h1>Task Statistics</h1>
    <p>Total tasks: {summary['total_tasks']}</p>
    <p>Completed tasks: {summary['completed_tasks']}</p>
    <p>Average priority: {summary['average_priority']}</p>
    """

    return HttpResponse(html)
