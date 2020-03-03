from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core import serializers as json_serializer
import json 
from datetime import date, datetime
from django.http import HttpResponse
from .utilities import Utilities
from .pagination import *
from rest_framework import generics
import os
import imghdr
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import authenticate,login,logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
# from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from .models import *
from django.contrib.auth.models import User
from .serializers import *
from django.conf import settings
from django.utils import timezone

class UserSignup(APIView):

    def post(self, request, format=None):
        response_dict = dict()
        try:
            request_post = json.loads(request.body)
        except Exception as e:
            get_response = Utilities.get_response(False,'empty post','empty post')
            return Response(get_response)
        try:
            _name = request_post['name']
            if _name == "":
                return Response(Utilities.get_response(False,'name field is empty','name field is empty'))
            _email =  request_post['email']
            if request_post['password'] == "":
                return Response(Utilities.get_response(False,'password field is empty','password field is empty'))
            _password = Utilities.get_hash(request_post['password'])
            
            verify = Utilities.signup_verify_email(_email) 
            if not verify[0]:
                raise Exception(verify[1])
            response_dict= Utilities.get_response(True,'Signup Successful','Signup Successful')    
        except Exception as e:
            response_dict['success'] = False
            response_dict['user_message'] = 'Please enter ' + str(e).strip("/'")
            response_dict['dev_message'] = str(e).strip("/'") + ' not entered' + ' Exception: ' + str(e)
            if str(e) == 'Valid Email':
                response_dict['dev_message']  = str(e).strip("/'") + ' not entered' + ' Exception: ' + 'Invalid Email' 
            response = response_dict
            return Response(response)    
        try: 
            auth_user = User.objects.create_user(username=_email,email= _email, password= request_post['password'])
            auth_user.save()
            user_obj = Users(user=auth_user,name= _name, user_type="customer",email=_email,password=_password,phone=request_post['phone'])
            user_obj.save()
        except Exception as e: 
            response_dict = Utilities.get_response(False, 'Registration Unsuccessful', 'could not save user.') 
        return Response(response_dict)


class Login(APIView):
    def post(self, request, format=None):    
        response_dict = dict()
        try:
            request_post = json.loads(request.body)
        except Exception as e:
            get_response = Utilities.get_response(False,'Please provide email and password','email and password missing')
            return Response(get_response)
        try:
            _email =  request_post['email']
            _password = request_post['password']
            verify = Utilities.login_verify_email(_email)
            if not verify[0]:
                raise Exception(verify[1])   
        except Exception as e:
            response_dict = Utilities.get_response(False, 'Please enter ' + str(e).strip("/'"),str(e).strip("/'") + ' not entered' + ' Exception: ' + str(e))
            if str(e) == 'Valid Email':
                response_dict['dev_message']  = str(e).strip("/'") + ' not entered' + ' Exception: ' + 'Invalid Email'  
            elif str(e) == 'Email not found':
                response_dict['user_message'] = str(e).strip("/'")
                response_dict['dev_message']  = str(e).strip("/'")
            elif str(e) == 'Account confirmation pending':
                response_dict['user_message'] = str(e).strip("/'")
                response_dict['dev_message']  = str(e).strip("/'")

            response = json.dumps(response_dict)
            return Response(response_dict) 
            
        if not Utilities.login_verify_password(_password,_email):
            response_dict =Utilities.get_response(False,'Incorrect Password','Incorrect Password')
            return Response(response_dict)
        auth_user = authenticate(username=_email, password=_password)
        
        if not auth_user:
            get_response = Utilities.get_response(False,'Invalid Credentials','Invalid Credentials')
            return Response(get_response)
        if auth_user.is_active:
            login(request, auth_user)
            token, _ = Token.objects.get_or_create(user=auth_user)
            response_dict = Utilities.get_response(True,'Signin successful', 'Signin successful')
            response_dict['name']  = verify[3]
            response_dict['token'] = token.key
            if verify[2] == 'company_admin':        
                response_dict['company_id'] = verify[4]  
                response_dict['permalink'] = verify[5]
                response_dict['user_type'] = verify[2]
            elif verify[2] == 'customer': 
                response_dict['user_id'] = verify[4]  
                response_dict['user_type'] = verify[2]     
        return Response(response_dict)


class Logout(APIView):

    def post(self,request,format=None):
        logout(request)
        return Response(Utilities.get_response(True,'Logout successful','Logout successful'))

        response_dict = dict()
        print( request.session['email'])
        try:
            del request.session['email']
            response_dict["success"] = True
            response_dict["user_message"] = 'Logout Successful'
            response_dict["dev_message"] = 'Logout Successful'
        except KeyError:
            response_dict["success"] = False
            response_dict["user_message"] = 'Logout Failed'
            response_dict["dev_message"] = 'Logout Failed ' + str(KeyError)
        response = json.dumps(response_dict)
        return Response(response)

class ToursDetail(generics.GenericAPIView):
    serializer_class = ToursSerializer
    def get(self,request,tour_id):
        try: 
            tour_obj = Tours.objects.get(id=tour_id)
        except Exception as e:
            return Response(Utilities.get_response(False,"tour id does not exist","tour id does not exist"))
        serializer = self.get_serializer(tour_obj,many=False)
        return Response(serializer.data)
    
    def put(self,request,tour_id):
        return Response()

class ToursList(generics.GenericAPIView):
    serializer_class = ToursSerializer 

    def post(self,request,format=None):
        try:
            request_post = json.loads(request.body)
        except Exception as e:
            return Response(Utilities.get_response(False,"Empty post","Empty post"))
        if "name" not in request_post:
            return Response(Utilities.get_response(False,"Name is missing","Name is missing"))
        if "start_date" not in request_post:
            return Response(Utilities.get_response(False,"start date is missing","start date is missing"))
        if "end_date" not in request_post:
            return Response(Utilities.get_response(False,"end date is missing","end date is missing"))
        start = datetime.strptime(request_post['start_date'],"%m/%d/%Y")
        end = datetime.strptime(request_post['end_date'],"%m/%d/%Y")
        tour_obj = Tours(name=request_post['name'],start_date=start,end_date=end)
        tour_obj.save()
        return Response(Utilities.get_response(True,"Tour created","Tour created"))

    def get(self,request,format=None):
        tour_objects = Tours.objects.all()
        serializer = self.get_serializer(tour_objects,many=True)
        return Response(serializer.data)

class PlacesList(generics.GenericAPIView):
    serializer_class = PlacesSerializer
    def get(self,request,format=None):
        place_objects = Places.objects.all()
        serializer = self.get_serializer(place_objects,many=True)
        return Response(serializer.data)
    
    def post(self,request,format=None):
        try:
            request_post = json.loads(request.body)
        except Exception as e:
            return Response(Utilities.get_response(False,"Empty post","Empty post"))
        if "name" not in request_post:
            return Response(Utilities.get_response(False,"Name is missing","Name is missing"))
        if "address" not in request_post:
            return Response(Utilities.get_response(False,"address is missing","address is missing"))
        if "description" not in request_post:
            return Response(Utilities.get_response(False,"description is missing","description is missing"))
        place_obj = Places(name=request_post['name'],address=request_post['address'],description=request_post['description'])
        place_obj.save()
        return Response(Utilities.get_response(True,"Place created","Place created"))

class PlacesDetail(generics.GenericAPIView):
    serializer_class = PlacesSerializer
    def get(self,request,place_id):
        try: 
            place_obj = Places.objects.get(id=place_id)
        except Exception as e:
            return Response(Utilities.get_response(False,"place id does not exist","place id does not exist"))
        serializer = self.get_serializer(place_obj,many=False)
        return Response(serializer.data)
    
    def put(self,request,place_id):
        return Response()
    

class UpcomingTours(generics.GenericAPIView):
    serializer_class = ToursSerializer
    def get(self,request,format=None):
        tours_obj = Tours.objects.filter()
        tours_obj = tours_obj.exclude(start_date__lt=timezone.now())
        serializer = self.get_serializer(tours_obj,many=True)
        return Response(serializer.data)


class AddFollowers(generics.GenericAPIView):
    serializer_class = UsersSerializer
    def post(self,request,user_id):
        try:
            request_post = json.loads(request.body)
        except Exception as e:
            return Response(Utilities.get_response(False,"Empty post","Empty post"))
        try: 
            user_obj = Users.objects.get(id=user_id)
        except Exception as e: 
            return Response(Utilities.get_response(False, "Invalid Id","Invalid Id"))
        if "follower_id" not in request_post:
            return Response(Utilities.get_response(False,"Follower id does not exist","Follower does not exist"))
        if request_post['followed_id'] == user_id:
            return Response(Utilities.get_response(False,"Can't follow yourself","Can't follow yourself"))
        try: 
            followed_obj = Users.objects.get(id=request_post['followed_id'])
        except Exception as e: 
            return Response(Utilities.get_response(False, "Invalid follower id","Invalid follower id"))
        if len(Followers.objects.filter(follower=user_obj,followed=followed_obj)) == 1:
            return Response(Utilities.get_response(False,"already a follower","already a follower"))
        follower_obj = Followers(follower = user_obj, followed = followed_obj)
        follower_obj.save()
        return Response(Utilities.get_response(True,"Follower added","Follower added"))

    def get(self,request,user_id):
        try:
            user_obj = Users.objects.get(id=user_id) 
        except: 
            return Response(Utilities.get_response(False,"user does not exist","user does not exist"))
        followers = Followers.objects.filter(follower=user_obj).values_list('followed',flat=True)
        user_obj = Users.objects.filter(id__in=followers)
        serializer = self.get_serializer(user_obj,many=True)
        return Response(serializer.data)

class AddActivities(generics.GenericAPIView):
    serializer_class = ActivitiesSerializer
    def post(self,request,tour_id):
        try: 
            request_post = json.loads(request.body)
        except Exception as e:
            return Response(Utilities.get_response(False,"empty post","empty post"))
        try: 
            tour_obj = Tours.objects.get(id=tour_id)
        except: 
            return Response(Utilities.get_response(False,"tour does not exist","tour does not exist"))
        if "name" not in request_post:
            return Response(Utilities.get_response(False,"name does not exist","name does not exist"))
        if "description" not in request_post:
            return Response(Utilities.get_response(False,"description does not exist","description does not exist"))
        activity_obj = Activities(name=request_post['name'],description=request_post['description'])
        activity_obj.save()
        return Response(Utilities.get_response(True,"Activity added","Activity added"))

    def get(self,request,tour_id):
        try: 
            tour_obj = Tours.objects.get(id=tour_id)
        except: 
            return Response(Utilities.get_response(False,"tour does not exist","tour does not exist"))
        activities_obj = Activities.objects.filter(tour_id=tour_obj)
        serializer = self.get_serializer(activities_obj,many=True)
        return Response(serializer.data)

class AdventuresList(generics.GenericAPIView):
    serializer_class = AdventuresSerializer
    def post(self,request,user_id):
        try: 
            user_obj = Users.objects.get(id=user_id)
        except:
            return Response(Utilities.get_response(False,"user does not exist","user does not exist")) 
        try: 
            request_post = json.loads(request.body)
        except: 
            return Response(Utilities.get_response(False,"empty post","empty post"))
        if 'name' not in request_post:
            return Response(Utilities.get_response(False,"name field not found","name field not found"))
        if 'description' not in request_post:
            return Response(Utilities.get_response(False,"description field not found","description field not found"))
        if 'per_day' not in request_post:
            return Response(Utilities.get_response(False,"per_day field not found","per_day field not found"))
        if '_from' not in request_post:
            return Response(Utilities.get_response(False,"_from field not found","_from field not found"))
        if 'destination' not in request_post:
            return Response(Utilities.get_response(False,"destination field not found","destination field not found"))
        if 'start_date' not in request_post:
            return Response(Utilities.get_response(False,"start_date field not found","start_date field not found"))
        if 'end_date' not in request_post:
            return Response(Utilities.get_response(False,"end_date field not found","end_date field not found"))
        if 'budget' not in request_post:
            return Response(Utilities.get_response(False,"budget field not found","budget field not found"))
        try:
            start = datetime.strptime(request_post['start_date'],"%m/%d/%Y")
            end = datetime.strptime(request_post['end_date'],"%m/%d/%Y")
        except: 
            return Response(Utilities.get_response(False,"date format is invalid","date format is invalid"))
        adventure_obj = Adventures(user_id=user_obj,budget=request_post['budget'],description=request_post['description'],name=request_post['name'],per_day=request_post['per_day'],_from=request_post['_from'],destination=request_post['destination'],start_date=start,end_date=end)        
        adventure_obj.save()
        return Response(Utilities.get_response(True,"Adventure added","Adventure added"))

    def get(self,request,user_id):
        try: 
            user_obj = Users.objects.get(id=user_id)
        except:
            return Response(Utilities.get_response(False,"user does not exist","user does not exist")) 
        adventure_objects = Adventures.objects.filter(user_id=user_obj)
        serializer = self.get_serializer(adventure_objects,many=True)
        return Response(serializer.data)

class AddTours(generics.GenericAPIView):
    serializer_class = ToursSerializer
    def post(self,request,user_id):
        try: 
            user_obj = Users.objects.get(id=user_id)
        except: 
            return Response(Utilities.get_response(False,"user does not exist","user does not exist"))
        try:
            request_post = json.loads(request.body)
        except:
            return Response(Utilities.get_response(False,"empty post","empty post"))
        if "tour_id" not in request_post:
            return Response(Utilities.get_response(False,"tour id is missing"))
        try: 
            tour_obj = Tours.objects.get(id=request_post['tour_id'])
        except: 
            return Response(Utilities.get_response(False,"tour does not exist","tour does not exist"))
        visited_obj = VisitedTours(user_id=user_obj,tour_id=tour_obj)
        visited_obj.save()
        return Response(Utilities.get_response(True,"tour added to visited","tour added to visited"))

    def get(self,request,user_id):
        try: 
            user_obj = Users.objects.get(id=user_id)
        except: 
            return Response(Utilities.get_response(False,"user does not exist","user does not exist"))
        visited_objects = VisitedTours.objects.filter(user_id=user_obj).values_list('tour_id',flat=True)
        tour_objects = Tours.objects.filter(id__in=visited_objects)
        serializer = self.get_serializer(tour_objects,many=True)
        return Response(serializer.data)
