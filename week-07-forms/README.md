# Week 07: Django Forms

## 🎯 Learning Objectives

- Create and validate forms with Django Forms
- Use ModelForms for database-backed forms
- Handle file uploads
- Implement custom form validation
- Work with formsets

## 📚 Required Reading

| Resource                                                                       | Section   | Time   |
| ------------------------------------------------------------------------------ | --------- | ------ |
| [Working with Forms](https://docs.djangoproject.com/en/5.0/topics/forms/)      | Full page | 45 min |
| [ModelForms](https://docs.djangoproject.com/en/5.0/topics/forms/modelforms/)   | Full page | 30 min |
| [Form Validation](https://docs.djangoproject.com/en/5.0/ref/forms/validation/) | Full page | 30 min |

---

## Key Concepts

### Form Types

```python
# tasks/forms.py
from django import forms
from .models import Task, Category


# Basic Form (not tied to model)
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)


# ModelForm (tied to model)
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'status', 'category', 'due_date', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def clean_title(self):
        """Custom field validation."""
        title = self.cleaned_data['title']
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters.")
        return title

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        due_date = cleaned_data.get('due_date')

        if status == 'completed' and due_date and due_date > timezone.now().date():
            raise forms.ValidationError(
                "Completed tasks cannot have a future due date."
            )
        return cleaned_data
```

### Using Forms in Views

```python
# Function-based view
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


# Class-based view
class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task_list')
```

### Form Template

```html
{% extends "base.html" %} {% block content %}
<h1>{% if form.instance.pk %}Edit{% else %}Create{% endif %} Task</h1>

<form method="post" novalidate>
  {% csrf_token %} {% for field in form %}
  <div class="mb-3">
    <label for="{{ field.id_for_label }}" class="form-label">
      {{ field.label }} {% if field.field.required %}<span class="text-danger"
        >*</span
      >{% endif %}
    </label>
    {{ field }} {% if field.errors %}
    <div class="invalid-feedback d-block">
      {% for error in field.errors %}{{ error }}{% endfor %}
    </div>
    {% endif %} {% if field.help_text %}
    <small class="form-text text-muted">{{ field.help_text }}</small>
    {% endif %}
  </div>
  {% endfor %}

  <button type="submit" class="btn btn-primary">Save</button>
  <a href="{% url 'tasks:task_list' %}" class="btn btn-secondary">Cancel</a>
</form>
{% endblock %}
```

---

## 📋 Submission Checklist

- [ ] TaskForm with custom validation
- [ ] Form rendering with error display
- [ ] File upload form (optional)
- [ ] Formset for bulk editing (optional)

---

**Next**: [Week 08: Admin →](../week-08-admin/README.md)
