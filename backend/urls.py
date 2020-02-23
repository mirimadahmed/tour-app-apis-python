from django.urls import include, path
from rest_framework import routers
from . import views
from django.conf.urls.static import static
from django.conf.urls import include
from django.conf import settings

urlpatterns = [
    path('signup/', views.UserSignup.as_view()),
    path('login/',views.Login.as_view()),
    path('logout/',views.Logout.as_view()),
]