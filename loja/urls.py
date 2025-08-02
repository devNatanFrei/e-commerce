

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('pedido/', include('pedido.urls')),
    path('perfil/', include('perfil.urls')),
    path('', include('produto.urls')),
    # path('admin/', admin.site.urls),
]


if settings.DEBUG:
 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    

    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    
    
    
  # urlpatterns += [
    #     path('admin/', admin.site.urls),
    # ]
    