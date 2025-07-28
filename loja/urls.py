from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('pedido/', include('pedido.urls')),
    path('perfil/', include('perfil.urls')),
    path('', include('produto.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += [
        path('meu-admin/', admin.site.urls),
    ]
    

    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
