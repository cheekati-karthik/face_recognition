"""
URL configuration for facerecognition project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path,include
from .views import upload_photos, upload_success,home,training,face_recognition_view,studentattendance,details,staffattendance
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('upload/', upload_photos, name='upload_photos'),
    path('success/', upload_success, name='success'),
    path('training/',training, name='training'),
    path('studentattendance/',studentattendance, name='studentattendance'),
    path('staffattendance/',staffattendance, name='staffattendance'),
    path('details/',details, name='details'),
    path('face_recognition/', face_recognition_view, name='face_recognition'),
]
