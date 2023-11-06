from django.shortcuts import render, redirect
from .models import Todo
from django.forms import ModelForm

class TodoForm(ModelForm):
    class Meta:
        model = Todo
        fields = ['title']

def index(request):
     todos = Todo.objects.all()
     if request.method == 'POST':
         new_todo = Todo(
             title = request.POST['title']
         )
         new_todo.save()
         return redirect('/')

     return render(request, 'index.html', {'todos':todos})

def update(request, id):
     todo = Todo.objects.get(pk=id)
     form = TodoForm(request.POST or None, instance=todo)
     if form.is_valid():
          form.save()
          return redirect('/')
     return render(request, 'todo_form.html', {'form':form})
     

def delete(request, id):
     todo = Todo.objects.get(pk=id)
     todo.delete()
     return redirect('/')

