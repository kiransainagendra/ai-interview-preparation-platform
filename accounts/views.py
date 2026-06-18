from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm
from resumes.models import Resume


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def dashboard(request):
    resumes = Resume.objects.filter(user=request.user).order_by('-uploaded_at') if request.user.is_authenticated else []

    context = {
        'resumes': resumes,
        'total_resumes': resumes.count() if request.user.is_authenticated else 0,
    }

    return render(request, 'accounts/dashboard.html', context)