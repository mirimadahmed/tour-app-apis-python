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
    path('tours/',views.ToursList.as_view()),
    path('tours/<tour_id>/',views.ToursDetail.as_view()),
    path('places/',views.PlacesList.as_view()),
    path('places/<place_id>/',views.PlacesDetail.as_view()),
    path('upcoming_tours/',views.UpcomingTours.as_view()),
    path('friends/<user_id>/',views.AddFollowers.as_view()),
    path('adventures/<user_id>/',views.AdventuresList.as_view()),
    path('visited_tours/<user_id>/',views.AddTours.as_view()),
]