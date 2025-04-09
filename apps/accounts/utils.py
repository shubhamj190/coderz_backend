from apps.accounts.models.user import UserDetails
from apps.accounts.models.user import UsersIdentity as User
from rest_framework import status
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from rest_framework.response import Response
import requests
from requests.auth import HTTPBasicAuth
import logging
from rest_framework import status
from django.forms.models import model_to_dict
from django.db import transaction
from apps.accounts.models.user import UserMaster
from django.contrib.auth.hashers import make_password

ENC_KEY = "4k2bv6CRCbCYoVM9CfpIzjh2slagTK5N"
QuestApi = "https://api.questplus.in/"
QuestWeb = "https://admin.questplus.in/"

def user_name_creator(user_type, user):
    UserName = None
    if user_type == 'Learner':
        if user:
            grade_obj=user.details.GradeId
            # division_obj=user.details.DivisionId

            # For student users, expect additional fields to generate a username.
            roll_number = UserDetails.objects.filter(GradeId=grade_obj).count() + 1
            if not roll_number:
                raise ValueError("roll_number must be provided for student user creation")
            grade_str = (grade_obj.GradeId if hasattr(grade_obj, 'GradeId') else str(grade_obj)).replace(" ", "") if grade_obj else ""
            # division_str = (division_obj.DivisionName if hasattr(division_obj, 'DivisionName') else str(division_obj)).replace(" ", "") if division_obj else ""
            if not UserName:
                UserName = f"L{roll_number}{grade_str}"
    else:
        # For admin/teacher users, generate a sequential username if not provided.
        if user:
            # Use a prefix based on the user_type.
            prefix_map = {'Admin': 'A', 'Teacher': 'F'}
            prefix = prefix_map.get(user_type, 'S')
            count = User.objects.all().count()
            UserName = f"{prefix}{count + 1:03d}"
    return UserName

def create_response(
    payload=None,
    message="Internal Server Error",
    status=status.HTTP_200_OK,
    pager=None,
     **kwargs
):
    if payload is None:
        payload = {}
    response = {"status": status, "message": message}
    if len(payload):
        response["payload"] = payload
    if pager:
        response["pager"] = pager
    for key, value in kwargs.items():
        response[key] = value    
    return Response(data=response, status=status)

def encrypt_AES_CBC(plaintext):
    enc_key = ENC_KEY
    iv = get_random_bytes(16)
    enc_key = bytes(enc_key, "utf-8")
    cipher = AES.new(enc_key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(bytes(plaintext, "utf-8"), AES.block_size))
    return iv.hex() + ":" + ciphertext.hex()


def decrypt_AES_CBC(plaintext):
    enc_key = ENC_KEY
    enc_key = bytes(enc_key, "utf-8")
    data = plaintext.split(":")
    iv = bytes.fromhex(data[0])
    ciphertext = bytes.fromhex(data[1])
    cipher = AES.new(enc_key, AES.MODE_CBC, iv)
    decipheredtext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decipheredtext.decode()

def UniversalAuthenticationHandeler(
    username, password, platform, isLogger, moduleName, eventName, dataId, DeviceId
):
    try:
        if platform == 0:
            response = requests.get(
                "{}Auth/GetAuthenticateUser?Username={}&Password={}&isLogger={}&moduleName={}&eventName={}&dataId={}".format(
                    QuestWeb,
                    username,
                    password,
                    isLogger,
                    moduleName,
                    eventName,
                    dataId,
                ),
                verify=False,  # remove later
            )
        elif platform == 1:
            headers = {}
            if DeviceId:
                headers = {"DeviceId": DeviceId}
            response = requests.post(
                "{}QuestUser/UserUnifiedLogin".format(QuestApi),
                auth=HTTPBasicAuth(username=username, password=password),
                headers=headers,
                verify=False,  # remove later
            )
        elif platform == 2:
            response = requests.post(
                "{}QuestUser/AuthenticateUser".format(QuestApi),
                auth=HTTPBasicAuth(username=username, password=password),
                verify=False,  # remove later
            )
        else:
            raise TypeError("Invalid platform ID")
        if response.status_code != 200:
            return False, create_response(
                message="Explicit User Authentication Failed",
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = response.json()
        return True, data
    except TypeError as e:
        logging.exception(e)
        return False, create_response(
            message="Invalid Platform Id", status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logging.exception(e)
        return False, create_response(
            message="Explicit User Authentication Failed",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def registerUser(data):
    try:
        with transaction.atomic():
            data = data
            username = data.get("username")
            email = data.get("Email")
            first_name = data.get("first_name", "")
            last_name = data.get("last_name", "")
            phone_number = data.get("phone_number")
            NormalizedUserName = data.get("NormalizedUserName")
            NormalizedEmail = data.get("NormalizedEmail")
            password = data.get("password")

            print("*" * 10, username, email, password)

            if not username or not email or not password:
                return create_response(
                    {"error": "All fields are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if UserMaster.objects.filter(username=username, IsDeleted=False).exists():
                return create_response(
                    {"error": "Username already taken"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = UserMaster.objects.create(
                username=username,
                email=email,
                password=make_password(password),  # Hash the password
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                NormalizedEmail=NormalizedEmail,
                NormalizedUserName=NormalizedUserName,
            )
            user.save()
            user_dict = model_to_dict(user)
            return (
                create_response(
                    message="User registered successfully",
                    status=status.HTTP_201_CREATED,
                    payload=user_dict,
                ),
                user,
            )
    except Exception as e:
        logging.exception(e)
        return create_response(
            message="User registration failed",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def UniversalLogoutHandler(token, isLogger, moduleName, eventName, dataId, platform):
    try:
        if platform == 0:
            response = requests.get(
                "{}Auth/Logout?Token={}&isLogger={}&moduleName={}&eventName={}&dataId={}".format(
                    QuestWeb,
                    token,
                    isLogger,
                    moduleName,
                    eventName,
                    dataId,
                ),
                verify=False,  # remove later
            )
        elif platform == 1:
            response = requests.get(
                "{}QuestUser/Logout".format(QuestApi),
                # auth=HTTPBasicAuth(username=username, password=password), #! pass token as bearer token
                headers={"Authorization": "Bearer {}".format(token)},
                verify=False,  # remove later
            )
        elif platform == 2:
            response = requests.get(
                "{}QuestUser/Logout".format(QuestApi),
                # auth=HTTPBasicAuth(username=username, password=password), #! pass token as bearer token
                headers={"Authorization": "Bearer {}".format(token)},
                verify=False,  # remove later
            )
        else:
            raise TypeError("Invalid platform ID")
        if response.status_code != 200:
            return False, create_response(
                message="Explicit User Logout Failed",
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = response.json()
        return True, data
    except TypeError as e:
        logging.exception(e)
        return False, create_response(
            message="Invalid Platform Id", status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logging.exception(e)
        return False, create_response(
            message="Explicit User Logout Failed",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
