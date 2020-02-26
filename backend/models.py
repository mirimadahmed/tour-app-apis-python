# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import django.utils.timezone
from django.contrib.auth.models import User

class Users(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,null=False)
    # address = models.CharField(max_length=200,null=True)
    phone = models.CharField(max_length=50,null=True)
    email = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=200,null=True)
    user_type = models.CharField(max_length=50, null=True)

    creation_date = models.DateTimeField(default= django.utils.timezone.now )
    last_modified = models.DateTimeField( auto_now = True )

class Friends(models.Model):
    id = models.AutoField(primary_key=True)
    user_1 = models.ForeignKey('Users',on_delete=models.PROTECT,null=True)
    user_1 = models.ForeignKey('Users',on_delete=models.PROTECT,null=True)

    creation_date = models.DateTimeField(default= django.utils.timezone.now )
    last_modified = models.DateTimeField( auto_now = True )

class Places(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,null=False)
    address = models.CharField(max_length=200,null=True)
    description = models.CharField(max_length=1000,null=True)
    creation_date = models.DateTimeField(default= django.utils.timezone.now )
    last_modified = models.DateTimeField( auto_now = True )

class Tours(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,null=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

class Activities(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,null=False)
    tour_id = models.ForeignKey('Tours',on_delete=models.PROTECT,null=True)

class Memories():
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,null=False)
    tour_id = models.ForeignKey('Tours',on_delete=models.PROTECT,null=True)