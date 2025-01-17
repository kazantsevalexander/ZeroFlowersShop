from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Автоматически логиним новосозданного пользователя:
            login(request, user)
            return redirect('product_list')  # куда перенаправить после успешной регистрации
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def logout_request(request):
    if request.method == 'POST':
        logout(request)
        return redirect('product_list')
    return render(request, 'accounts/logout.html')
