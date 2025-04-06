from django.shortcuts import render

# Create your views here.
def Articles(request):
    return render(request, 'blog/articles.html')