from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from ai_chatbot import views as ai_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frontend.urls')),
    path('patient-dashboard/', include(('patientdashboard.urls', 'patientdashboard'), namespace='patientdashboard')),
    path('practitioner-dashboard/', include(('practitionerdashboard.urls', 'practitionerdashboard'), namespace='practitionerdashboard')),
    path('chat/', include('chat.urls')),
    path('ai-chatbot/', include('ai_chatbot.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('generate-avatar-response/', ai_views.ask_avatar, name='generate_avatar_response'),  # Direct route for avatar
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
