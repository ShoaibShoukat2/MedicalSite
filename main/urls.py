from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frontend.urls')),
    path('patient-dashboard/', include(('patientdashboard.urls', 'patientdashboard'), namespace='patientdashboard')),
    path('practitioner-dashboard/', include(('practitionerdashboard.urls', 'practitionerdashboard'), namespace='practitionerdashboard')),
    path('chat/', include('chat.urls')),
    path('auth/', include('social_django.urls', namespace='social')),

]



# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # ✅ corrected line












