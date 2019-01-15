"""django_rest_network URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include, re_path
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Network API')
urlpatterns = [
    path(r'', schema_view),
    path('admin/', admin.site.urls),
    path(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(r'api-token-auth/', obtain_jwt_token, name='create-token'),
    path(r'^api-token-refresh/', refresh_jwt_token),
    path(r'^api-token-verify/', verify_jwt_token),

    path(r'posts/', include('posts.urls')),
    path(r'users/', include('users.urls')),

    ]
