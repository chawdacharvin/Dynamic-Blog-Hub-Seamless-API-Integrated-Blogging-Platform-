
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('posts.urls')),
    path('', include('posts.urls')),
    path('', include('social_django.urls', namespace='social')),
]
