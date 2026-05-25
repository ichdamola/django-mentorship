from django.http import HttpRequest, HttpResponse


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<h1>TaskMaster</h1><p>Welcome to your task manager!</p>")


def task_list(request: HttpRequest) -> HttpResponse:
    tasks = [
        {"id": 1, "title": "Learn Django", "status": "in_progress"},
        {"id": 2, "title": "Build an app", "status": "pending"},
    ]
    html = "<h1>Tasks</h1><ul>"
    for task in tasks:
        html += f"<li><a href='/tasks/{task['id']}/'>{task['title']}</a> - {task['status']}</li>"
    html += "</ul>"
    return HttpResponse(html)


def task_detail(request: HttpRequest, task_id: int) -> HttpResponse:
    return HttpResponse(f"<h1>Task #{task_id}</h1>")


def about(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<h1>About Page</h1>")


def stats(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<h1>Task statistics</h1>")
