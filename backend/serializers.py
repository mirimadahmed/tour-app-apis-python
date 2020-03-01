from rest_framework import serializers
from .models import *

class ToursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tours
        fields = "__all__"

class PlacesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Places
        fields = "__all__"

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = "__all__"

class ActivitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activities
        fields = "__all__"

class AdventuresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adventures
        fields = "__all__"