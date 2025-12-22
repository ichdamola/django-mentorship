# Week 09: Authentication & Authorization

## 🎯 Learning Objectives

- Implement user registration and login
- Use Django's authentication system
- Create custom user models
- Handle permissions and groups
- Protect views with decorators and mixins

## 📚 Required Reading

| Resource                                                                                                | Section   | Time   |
| ------------------------------------------------------------------------------------------------------- | --------- | ------ |
| [Authentication](https://docs.djangoproject.com/en/5.0/topics/auth/)                                    | Full page | 45 min |
| [Custom User Model](https://docs.djangoproject.com/en/5.0/topics/auth/customizing/)                     | Full page | 30 min |
| [Permissions](https://docs.djangoproject.com/en/5.0/topics/auth/default/#permissions-and-authorization) | Full page | 20 min |

---

## Key Concepts

### Custom User Model (Always do this first!)

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model - extend as needed."""
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)

    def __str__(self):
        return self.email or self.username
```

```python
# config/settings.py
AUTH_USER_MODEL = 'accounts.User'
```

### Authentication Views

```python
# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),

    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
```

### Protecting Views

```python
# Function-based views
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

@permission_required('tasks.add_task')
def task_create(request):
    ...

# Class-based views
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    ...

class TaskDeleteView(PermissionRequiredMixin, DeleteView):
    model = Task
    permission_required = 'tasks.delete_task'
```

### User-Specific Data

```python
# Add owner to Task model
class Task(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    ...

# Filter by user in views
class TaskListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
```

---

## 📋 Submission Checklist

- [ ] Custom User model created
- [ ] Registration and login working
- [ ] Views protected with login_required
- [ ] Tasks filtered by owner
- [ ] Logout functionality
- [ ] Profile page

---

**Next**: [Week 10: REST API →](../week-10-rest-api/README.md)
