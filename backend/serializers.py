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