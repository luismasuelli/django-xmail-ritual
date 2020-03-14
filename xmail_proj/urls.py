from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from .views import sample

urlpatterns = [
    path('sample', sample),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
