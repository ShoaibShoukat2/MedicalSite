"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static  # Import static
from django.conf import settings

from main import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frontend.urls')),
    path('patient-dashboard/', include('patientdashboard.urls', namespace='patientdashboard')),
    
    path('practitioner-dashboard/', include('practitionerdashboard.urls', namespace='practitionerdashboard')),
    path('chat/', include('chat.urls')),


    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL)
    
    
    
    
    