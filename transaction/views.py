from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.


# @login_required
# def home(request):
#     return render(request, 'home.html')

def home(request):
    return render(request, 'index.html')


def view_404(request, *args, **kwargs):
    return render(request, 'partial/404.html', {'title': 'Oops! Page Not Found!!'}, status=404)
