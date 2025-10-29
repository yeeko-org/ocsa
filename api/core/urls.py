from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect
from ocsa_legacy.admin import legacy_admin_site


admin.site.site_header = "Administración Catálogos OCSA"
admin.site.site_title = "Administración Catálogos OCSA"
admin.site.index_title = "Administración Catálogos OCSA"


urlpatterns = [
    path('', lambda request: redirect('admin/', permanent=False)),
    path('admin/', admin.site.urls),
    path('legacy_admin/', legacy_admin_site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('api.urls')),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
