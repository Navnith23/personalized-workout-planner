from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='base/landing.html'), name='landing'),
    path('accounts/', include('accounts.urls')),
    path('assessment/', include('assessment.urls')),
    path('plan/', include('programs.urls')),
    path('checkin/', include('progress.urls')),
    path('progress/', include('progress.urls_history')),

    # Static legal pages — required because we collect health data.
    path(
        'privacy/',
        TemplateView.as_view(template_name='base/privacy.html'),
        name='privacy',
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
