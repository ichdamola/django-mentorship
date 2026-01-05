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
    return HttpResponse(f"<h1>About</h1><p>Taskmaster is a simple project designed to create and manage tasks</p>")

def stats(request: HttpRequest) -> HttpResponse:
    
    tasks = [
        {"id": 1, "title": "Learn Django", "status": "in_progress"},
        {"id": 2, "title": "Build an app", "status": "pending"},
    ]
        
    pending = 0
    
    for task in tasks:
        if task["status"] == "pending":
            pending +=1
            
    return HttpResponse(f"You have {pending} pending tasks")