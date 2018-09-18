from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.default_login, name = 'default_login'),
    path('register', views.new_register, name = 'new_register'),
    path('logout', views.user_logout, name = 'user_logout'),
    path('home', views.home, name = 'home'),
    path('user/<slug:slug>', views.user_page, name = 'user_page'),
    path('search', views.search, name = 'search'),
    path('notifications', views.notifications, name = 'notifications'),
    path('create-group', views.create_group, name = 'create_group'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)