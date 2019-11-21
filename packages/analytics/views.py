from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home(request):
    return render(request, 'analytics/home.html')


@login_required
def add_code_to_site(request):
    return render(request, 'analytics/add-code-to-site.html')
