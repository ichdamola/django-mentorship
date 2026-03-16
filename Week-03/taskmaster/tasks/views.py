from django.http import (
    HttpRequest,
    HttpResponse,
    JsonResponse,
    HttpResponseRedirect,
    Http404,
    HttpResponseBadRequest,
)
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.core.paginator import Paginator
from django.contrib import messages
from .forms import TaskForm

from .models import Task, Category, Status, Priority


# # Basic view
# def task_list(request: HttpRequest) -> HttpResponse:
#     """List all tasks."""
#     tasks = Task.objects.select_related('category').all()

#     # Filter by status
#     status = request.GET.get('status')
#     if status:
#         tasks = tasks.filter(status=status)

#     # Build simple HTML response
#     html = "<h1>Tasks</h1>"
#     html += '<p><a href ="?status=pending">Pending</a> | '
#     html += '<p><a href ="?status=completed">Completed</a> | '
#     html += '<a href="?">All</a></p>'
#     html += "<ul>"

#     for task in tasks[:20]:
#         html += f'<li><a href="/tasks/{task.pk}/">{task.title}</a> - {task.status}</li>'
#     html += "</ul>"
#     html += '<p><a href="/tasks/create/">+ Create task</a></p>'
#     return HttpResponse(html)

# def task_detail(request: HttpRequest, pk: int) -> HttpResponse:
#     """Show task details."""
#     task = get_object_or_404(Task, pk=pk)

#     html = f"""
#     <h1>{task.title}</h1>
#     <p><strong>Status:</strong> {task.get_status_display()}</p>
#     <p><strong>Priority:</strong> {task.priority}</p>
#     <p><strong>Description:</strong> {task.description or 'No description'}</p>
#     <p><strong>Created:</strong> {task.created_at}</p>
#     <hr>
#     <a href="/tasks">← Back to list</a> |
#     <a href="/tasks/{task.pk}/delete/">Delete</a>
#     """

#     return HttpResponse(html)

# @csrf_exempt
# def task_create(request: HttpRequest) -> HttpResponse:
#     """Create a new task."""
#     if request.method == 'POST':
#         title = request.POST.get('title')
#         if title:
#             task = Task.objects.create(
#                 title=title,
#                 description=request.POST.get('description', ''),
#                 priority=int(request.POST.get('priority', 2)),
#             )
#             return redirect('tasks:task_detail', pk=task.pk)
#         else:
#             return HttpResponse("<p>Error: Title required</p>", status=400)

#     # Show simple form
#     html = """
#     <h1>Create Task</h1>
#     <form method="post">
#         <input type="hidden" name="csrfmiddlewaretoken" value="disabled">
#         <p>
#             <label>Title: <input type="text" name="title" required></label>
#         </p>
#         <p>
#             <label>Description:<br>
#             <textarea name="description" rows="4" cols="40"></textarea></label>
#         </p>
#         <p>
#             <label>Priority:
#             <select name="priority">
#                 <option value="1">Low</option>
#                 <option value="2" selected>Medium</option>
#                 <option value="3">High</option>
#             </select></label>
#         </p>
#         <button type="submit">Create</button>
#     </form>
#     <p><a href="/tasks">← Back to list</a></p>
#     """
#     return HttpResponse(html)

# @csrf_exempt
# def task_delete(request: HttpRequest, pk: int) -> HttpResponse:
#     """Delete a task."""
#     task = get_object_or_404(Task, pk=pk)

#     if request.method == 'POST':
#         task.delete()
#         return redirect('tasks:task_list')

#     html = f"""
#     <h1>Delete Task</h1>
#     <p>Are you sure you want to delete "{task.title}"?</p>
#     <form method="post">
#         <button type="submit">Yes, Delete</button>
#         <a href="/tasks/{task.pk}/">Cancel</a>
#     </form>
#     """
#     return HttpResponse(html)


# # # Delete with confirmation
# # @require_http_methods(["GET", "POST"])
# # def task_delete(request: HttpRequest, pk: int) -> HttpResponse:
# #     """Delete a task."""
# #     task = get_object_or_404(Task, pk=pk)

# #     if request.method == 'POST':
# #         task.delete()
# #         return redirect('tasks:task_list')


# #     return render(request, 'tasks/task_confirm_delete.html', {'task': task})
def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, "tasks/dashboard.html")


def task_list(request: HttpRequest) -> HttpResponse:
    """List all tasks with filtering and pagination."""
    tasks = Task.objects.select_related("category").prefetch_related("tags")

    # Filter by status (query parameter)
    status = request.GET.get("status")
    if status:
        tasks = tasks.filter(status=status)

    # Filter by category
    category_id = request.GET.get("category")
    if category_id:
        tasks = tasks.filter(category_id=category_id)

    # Pagination
    paginator = Paginator(tasks, 10)  # 10 tasks per page
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "statuses": Status.choices,
        "current_status": status,
        "current_category": category_id,
    }
    return render(request, "tasks/task_list.html", context)


# Detail view with 404 handling
def task_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Show task details."""
    task = get_object_or_404(Task, pk=pk)
    return render(request, "tasks/task_detail.html", {"task": task})


# Handle multiple HTTP methods
@require_http_methods(["GET", "POST"])
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, 'Task created!')
            return redirect('tasks:task_detail', pk=task.pk)
    else:
        form = TaskForm()

    return render(request, 'tasks/task_form.html', {'form': form})


# JSON response for API-like endpoints
def task_api_list(request: HttpRequest) -> JsonResponse:
    """Return tasks as JSON."""
    tasks = Task.objects.all().values("id", "title", "status", "priority", "created_at")
    return JsonResponse({"tasks": list(tasks)})


# Update with method restriction
@require_POST
def task_complete(request: HttpRequest, pk: int) -> HttpResponse:
    """Mark a task as complete."""
    task = get_object_or_404(Task, pk=pk)
    task.mark_complete()

    # Check if AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"status": "success", "task_id": pk})

    return redirect("tasks:task_detail", pk=pk)
    
# Delete with confirmation
@require_http_methods(["GET", "POST"])
def task_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete a task."""
    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        task.delete()
        return redirect("tasks:task_list")

    return render(request, "tasks/task_confirm_delete.html", {"task": task})


