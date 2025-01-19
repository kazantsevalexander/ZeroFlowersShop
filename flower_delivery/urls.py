from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shop.views import product_list  # Исправляем импорт, берем из приложения shop

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', include('shop.urls')),
    path('accounts/', include('accounts.urls')),
    path('', product_list, name='home'),  # Главная страница теперь указывает на shop.views.product_list

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)