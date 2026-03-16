from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),
    # Task CRUD
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/create/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/", views.task_detail, name="task_detail"),
    # path('tasks/<int:pk>/edit/', views.task_update, name='task_update'),
    path("tasks/<int:pk>/delete/", views.task_delete, name="task_delete"),
    # Task actions
    path("tasks/<int:pk>/complete/", views.task_complete, name="task_complete"),
    # path('tasks/<int:pk>/reopen/', views.task_reopen, name='task_reopen'),
    # Categories
    # path('categories/', views.category_list, name='category_list'),
    # path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    # API
    # path('api/tasks/', views.api_task_list, name='api_task_list'),
    # path('api/tasks/<int:pk>/', views.api_task_detail, name='api_task_detail'),
]
