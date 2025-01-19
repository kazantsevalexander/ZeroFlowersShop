from django.shortcuts import render

def home(request):
    return render(request, 'product_list.html')
