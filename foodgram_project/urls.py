from django.conf import settings
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path

handler404 = 'main.views.page_not_found'
handler500 = 'main.views.server_error'

urlpatterns = [
    path("about-spec/", views.flatpage, {"url": "/about-spec/"}, name="spec"),
    path("about-author/", views.flatpage, {"url": "/about-author/"}, name="author"),
    path("about/", include("django.contrib.flatpages.urls")),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('main.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
