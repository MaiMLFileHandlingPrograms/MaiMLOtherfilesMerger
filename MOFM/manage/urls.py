from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import MainMenu

app_name = 'manage'

urlpatterns = [
    path("", MainMenu.displayTop, name='top'), 
] #+ static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)