"""
URL configuration for summarizer_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]

from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from fileupload import views


urlpatterns = [
    # path('$', views.home, name='home'),
    # path('uploads/simple/', views.simple_upload, name='simple_upload'),
    path('form', views.simple_upload, name='simple_upload'),
    path('success_page', views.success_page, name='success_page'),
    path('file_updates', views.file_updates, name='file_updates'),
    path('link_page', views.link_page, name='link_page'),
    path('waiting_page', views.waiting_page, name='waiting_page'),
    path('run_iteration', views.run_iteration, name='run_iteration'),
    path('fetch_progress', views.fetch_progress, name='fetch_progress'),
    path('return_to_upload', views.return_to_upload, name = 'return_to_upload'),
    path('', views.login, name='login'),
    #path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
