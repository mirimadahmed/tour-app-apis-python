import hashlib, binascii, os
import re
from django.core import serializers as json_serializer
from django.forms.models import model_to_dict
from .models import *
import json
from datetime import date, datetime
import math
from rest_framework.authtoken.models import Token

class Utilities:
    
    @staticmethod
    def get_hash(password):
        """Hash a password for storing."""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                    salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify a stored password against one provided by user"""
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                    provided_password.encode('utf-8'), 
                                    salt.encode('ascii'), 
                                    100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password
    
    @staticmethod 
    def signup_verify_email(_email):
        string = "[^@]+@[^@]+\.[^@]+"
        if re.fullmatch(string, _email):
            try:
                db_user = Users.objects.get(email=_email)
                return (False, 'Unique Email')
            except Exception as e:
                return (True,'Valid Email')
        return (False, 'Valid Email')

    @staticmethod
    def login_verify_email(_email):
        string = "[^@]+@[^@]+\.[^@]+"
        if re.fullmatch(string, _email):
            try:
                db_user = Users.objects.get(email=_email)
                return (True,'Valid Email',db_user.user_type,db_user.name,db_user.id)                   
            except Exception as e:
                print(str(e))
                return (False,'Email not found')
        return (False,'Valid Email')

    @staticmethod 
    def login_verify_password(_password, _email):
        try:
            db_user = Users.objects.get(email=_email)
            if Utilities.verify_password(db_user.password,_password):
                return True
            else: 
                return False
        except Exception as e:
            # print(e)
            return False


    @staticmethod
    def get_response(success,usr_msg,dev_msg):
        response_dict =dict()
        response_dict['success'] = success
        response_dict['user_message'] = usr_msg
        response_dict['dev_message'] = dev_msg
        return response_dict


   