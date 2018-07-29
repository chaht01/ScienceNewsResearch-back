from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Examples:

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('cq.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
