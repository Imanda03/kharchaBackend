"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
import imp
from django.conf import settings
from django.conf.urls.static import static, serve
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_swagger.views import get_swagger_view
from django.conf.urls import url
from transaction.views import home



schema_view = get_swagger_view(title='Donation Platform API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls'), name="AuthenticationAPI"),
    path('api/v1/expensetracker/', include('transaction.urls'), name="ExpenseTrackerAPI"),
    path('swagger/', schema_view, name="SwaggerView"),
    path('__debug__/', include('debug_toolbar.urls')),
    # url(r'^media/(?P<path>.*)$', serve,
    #     {'document_root': settings.MEDIA_ROOT}),
    # url(r'^static/(?P<path>.*)$', serve,
    #     {'document_root': settings.STATIC_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


react_views = [
    # List all your react routes here
    "",
    "logout/",
    "register/",
    "login/",
    "accounts/",
    "manage/accounts/",
    "manage/accounts/<int:id>/",
    "create-account-book/",
    "accounts/<int:id>/",
    "profile/",
    "change-password/",
]

urlpatterns += [path(i, home, name='homepage') for i in react_views]
