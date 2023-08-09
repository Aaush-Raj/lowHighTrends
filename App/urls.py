from django.conf.urls import static
from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('stop_strategy', views.stopStrategy, name='stop_strategy'),
    path('stop-function/', views.stopStrategy, name='stop_function'),
    path('signup/', views.user_signup, name='signup'),
    path('user_details/', views.userDetails, name='user_details'),
    path('login/', views.user_login, name='login'),
        path('logout/', views.logout_view, name='logout'),




]
