from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', include('diary.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('gratitude/', include('gratitude.urls')),
    path('vitamin/', include('vitamin.urls', namespace='vitamin')),
    path('gut_health/', include('gut_health.urls', namespace='gut_health')),
    path('comfort/', include('comfort_list.urls')),
    path('nukazuke/', include('nukazuke.urls')),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += path('__debug__/', include('debug_toolbar.urls')),

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
