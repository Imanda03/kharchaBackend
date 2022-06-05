from rest_framework_simplejwt.views import TokenObtainPairView
from authentication.serializers import MyTokenObtainPairSerializer, CustomUserSerializer, CustomerSerializer, UserTokenSerializer, CustomTokenObtainSlidingSerializer, TokenVerificationSerializer, PasswordChangeSerializer,PasswordResetSerializer
from rest_framework.response import Response
from rest_framework import status, permissions
from authentication.models import CustomUser, UserToken, Customer
from authentication.permissions import IsAdminPermission, is_user_admin, is_user_customer
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import filters
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from authentication.utils import RandomStringTokenGenerator
from authentication.constants import DEFAULT_ASSETS_IMAGES_PATH, ADMIN_DOMAIN, CLIENT_DOMAIN
from django.template.loader import render_to_string
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView


def get_user_verification(data):
    email = data['email']
    users = CustomUser.objects.filter(email=email)
    if len(users) == 1:
        user = users[0]
        if not user.email_verified:
            return status.HTTP_406_NOT_ACCEPTABLE
        return status.HTTP_200_OK
    return status.HTTP_404_NOT_FOUND


def set_auth_cookie(resp):
    refresh = resp.data.get('refresh')
    resp.set_cookie(settings.SIMPLE_JWT.get('REFRESH_COOKIE_NAME'), refresh, max_age=settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME').total_seconds(), samesite=settings.SIMPLE_JWT.get('REFRESH_TOKEN_SAMESITE'), secure=settings.SIMPLE_JWT.get('REFRESH_TOKEN_SECURE'), httponly=settings.SIMPLE_JWT.get('REFRESH_TOKEN_HTTP_ONLY'))
    resp.data.pop('refresh')
    return resp


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomTokenObtainSlidingSerializer
    def post(self, request, *args, **kwargs):
        data = {}
        data['refresh'] = request.COOKIES.get(settings.SIMPLE_JWT.get("REFRESH_COOKIE_NAME"))
        serializer = self.get_serializer(data=data)
        try:
            if serializer.is_valid(raise_exception=True):
                resp = Response(serializer.validated_data, status=status.HTTP_200_OK)
                resp = set_auth_cookie(resp)
                return resp
        except:
            return Response({"refresh":"invalid or expired refresh token cookie"}, status=status.HTTP_401_UNAUTHORIZED)
        


class UserObtainTokenView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # request.PAYLOAD_SOURCE = 'User'
        # if(get_user_verification(request.data) == status.HTTP_406_NOT_ACCEPTABLE):
        #     return Response({"detail": "Inactive user. Please activate from email or contact us for support"}, status.HTTP_400_BAD_REQUEST)
        resp = super().post(request, *args, **kwargs)
        resp = set_auth_cookie(resp)
        return resp


# before login check register id of the device and make a model entry about device and the user (get, create or update)
# class CustomerObtainTokenView(TokenObtainPairView):
#     serializer_class = MyTokenObtainPairSerializer

#     def post(self, request, *args, **kwargs):
#         resp = super().post(request, *args, **kwargs)
#         resp = set_auth_cookie(resp)
#         return resp


class BlacklistView(APIView):
    """View for Logout """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get(settings.SIMPLE_JWT.get('REFRESH_COOKIE_NAME'))
            token = RefreshToken(refresh_token)
            token.blacklist()
            resp = Response(status=status.HTTP_205_RESET_CONTENT)
            resp.delete_cookie(settings.SIMPLE_JWT.get('REFRESH_COOKIE_NAME'))
            return resp
        except Exception as e:
            print(e)
            resp = Response(status=status.HTTP_400_BAD_REQUEST)
        return resp


class UserListView(ListAPIView):
    permission_classes = [IsAdminPermission]
    search_fields = ['first_name', 'last_name', 'email']
    filter_backends = (filters.SearchFilter,)
    queryset = CustomUser.users.all()
    serializer_class = CustomUserSerializer


class UserDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminPermission]
    queryset = CustomUser.users.all()
    serializer_class = CustomUserSerializer


class UserView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if is_user_admin(self.request):
            return CustomUser.objects.all()
        return Customer.objects.all()

    def get_serializer_class(self):
        if is_user_admin(self.request):
            return CustomUserSerializer
        return CustomerSerializer
    

    def get(self, request):
        if request.user.is_authenticated:
            instance = request.user
            serializer = self.get_serializer_class()
            if is_user_customer(request):
                try:
                    instance = Customer.objects.get(id=instance.id)
                except:
                    pass
            if instance is not None:
                serializer = serializer(instance)
                return Response(serializer.data)
            else:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            # except Exception:
            #         return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail":"Unauthorized User"}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request, format=None):
        if request.user.is_authenticated:
            instance = request.user
            if is_user_customer(request):
                try:
                    instance = Customer.objects.get(id=instance.id)
                except:
                    pass
            serializer = self.get_serializer_class()
            serializer = serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                obj = serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail":"Unauthorized User"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request):
        # if is_user_admin(request):
        #     user = request.user
        #     user.delete()
        #     return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail":"Forbidden!"}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request, format='json'):
        try:
            serializer = self.get_serializer_class()
            serializer = serializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                user = serializer.save()
                if user:
                    json = serializer.data
                    return Response(json, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as err:
            return Response(err.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exe:
            return Response({"detail": "Error creating user", "error": exe}, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeAPIView(APIView):
    permission_classes= [permissions.IsAuthenticated]
    def post(self,request, *args, **kwargs):
        data = request.data
        serializer = PasswordChangeSerializer(data=data, context={"request":request})
        if serializer.is_valid(raise_exception=True):
            user = request.user
            user.set_password(data['new_password1'])
            user.save()
            return Response({"detail":"Password Changed Successfully!"}, status=status.HTTP_202_ACCEPTED)

def checkValidity(data):
    if TokenVerificationSerializer(data=data).is_valid(raise_exception=True):
        user = CustomUser.objects.filter(id=data['identifier'])
        if (user.last() == None):
            return ({"detail": "User not found!"}, status.HTTP_404_NOT_FOUND)
        token = UserToken.objects.filter(
            user=user.last().id, key=data['token'])
        if (token.last() == None):
            return ({"detail": "Token not found!"}, status.HTTP_404_NOT_FOUND)
        if(not token.last().isValid()):
            token.last().delete()
            return ({"detail": "Token expired!"}, status.HTTP_400_BAD_REQUEST)
        if(token.last().key_type != int(data['type'])):
            return ({"detail": "Token type is not valid!"}, status.HTTP_400_BAD_REQUEST)
        return ({"detail": "Token is verified!"}, status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def isTokenValid(request):
    try:
        data = request.data
        msg, statusID = checkValidity(data)
        return Response(msg, statusID)
    except Exception as ex:
        return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def activateAccount(request):
    try:
        data = request.data
        msg, statusID = checkValidity(data)
        if(statusID == status.HTTP_200_OK):
            if(not int(data['type']) == 0):
                return Response({"detail": "Token type is not valid"}, status.HTTP_400_BAD_REQUEST)
            user = CustomUser.objects.filter(id=data['identifier']).last()
            user.email_verified = True
            user.save()
            token = UserToken.objects.filter(
                user=user.id, key=data['token']).last()
            token.delete()
            msg["detail"] = "Account activated"
        return Response(msg, statusID)
    except Exception as ex:
        print(ex)
        return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def resetPassword(request):
    data = request.data
    if(not int(data['type']) == 1):
        return Response({"detail": "Token type is not valid"}, status.HTTP_400_BAD_REQUEST)
    serializer = PasswordResetSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        msg, statusID = checkValidity(data)
        if(statusID == status.HTTP_200_OK):
            user = CustomUser.objects.filter(id=data['identifier']).last()
            user.set_password(data['new_password1'])
            user.save()
            token = UserToken.objects.filter(
                user=user.id, key=data['token']).last()
            token.delete()
            msg["detail"] = "Password reset successful."
        return Response(msg, statusID)
    # except Exception as ex:
    #     return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordAPIView(APIView):
    permission_classes=[permissions.AllowAny
    ]
    def post(self,request, *args, **kwargs):
        try:
            data = request.data
            if(data and 'email' in data):
                user = CustomUser.objects.filter(email=data['email'])
                if(user.first() == None):
                    return Response({"detail": "User not found for given email."}, status.HTTP_404_NOT_FOUND)
                userInstance = user.first()
                token = UserToken.objects.filter(
                    user=userInstance.id, key_type=1).order_by('-created_at')
                if(not token.first() == None):
                    latestToken = token.first()
                    if(latestToken.isValid()):
                        return Response({"detail": "Token already generated in last 1 hour. Please check your email."}, status.HTTP_400_BAD_REQUEST)
                    else:
                        for tok in token:
                            if not tok.isValid():
                                tok.delete()
                rand = RandomStringTokenGenerator()
                token = rand.generate_unique_token(model=UserToken, field="key")
                first_name = userInstance.first_name if (
                    len(userInstance.first_name) >= 1) else "User"
                from django.conf import settings
                assets_image_path = str(request.build_absolute_uri(
                    settings.MEDIA_URL + DEFAULT_ASSETS_IMAGES_PATH))
                client_domain = CLIENT_DOMAIN
                domain = ADMIN_DOMAIN
                if userInstance.role == 2:
                    domain = CLIENT_DOMAIN
                message = render_to_string('forget-password.html',
                                        {'username': first_name, 'domain': domain, 'client_domain': client_domain, 'token': token, 'identifier': userInstance.id, 'url': assets_image_path})
                mail = userInstance.send_mail(
                    subject=f"{settings.PROJECT_NAME} - Forget Password", message=message)
                if(mail == "success"):
                    data = {"user": userInstance.id, "key": token, "key_type": 1}
                    tokenSerializer = UserTokenSerializer(data=data)
                    if(tokenSerializer.is_valid(raise_exception=True)):
                        UserToken.objects.create(**tokenSerializer.validated_data)
                    return Response({"detail": "Password reset email sent!"}, status.HTTP_200_OK)
                else:
                    return Response({"detail": "Problem in sending email!"}, status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"email": "This field is required"}, status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            print(ex)
            return Response({"detail": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


# class CustomerCRUView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def get(self, request):
#         if request.user.is_authenticated:
#             try:
#                 # if is_user_admin(request.user):
#                 #     instance = CustomUser.objects.filter(pk=request.user.id).last()
#                 # elif is_user_customer(request.user):
#                 instance = Customer.objects.filter(pk=request.user.id).last()
#                 if instance is not None:
#                     serializer = CustomerSerializer(instance)
#                     return Response(serializer.data)
#                 else:
#                     return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
#             except Exception:
#                 return Response(status=status.HTTP_400_BAD_REQUEST)
#         return Response({"detail":"Unauthorized User"}, status=status.HTTP_401_UNAUTHORIZED)

#     def patch(self, request, format=None):
#         if request.user.is_authenticated:
#             instance = Customer.objects.filter(pk=request.user.id).last()
#             serializer = CustomerSerializer(
#                 instance, data=request.data, partial=True)
#             if(serializer.is_valid(raise_exception=True)):
#                 serializer.save()
#                 return Response(serializer.data)
#             else:
#                 return Response(status=status.HTTP_400_BAD_REQUEST)
#         return Response({"detail":"Unauthorized User"}, status=status.HTTP_401_UNAUTHORIZED)
#         # except serializers.ValidationError as ex:
#         #     return Response(ex.detail, status=status.HTTP_400_BAD_REQUEST)
#         # except Exception as ex:
#         #     return Response({"detail": ex}, status=status.HTTP_400_BAD_REQUEST)

#     def post(self, request, format='json'):
#         # try:
#         serializer = CustomerSerializer(
#             data=request.data, context={"request": request})
#         if serializer.is_valid(raise_exception=True):
#             user = serializer.save()
#             if user:
#                 json = serializer.data
#                 return Response(json, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         # except serializers.ValidationError as err:
#         #     return Response(err.detail, status=status.HTTP_400_BAD_REQUEST)
#         # except Exception:
#         #     return Response({"detail": "Error creating customer"}, status=status.HTTP_400_BAD_REQUEST)


# class CustomerListView(ListAPIView):
#     permission_classes = [IsAdminPermission]
#     search_fields = ['first_name', 'last_name', 'email']
#     filter_backends = (filters.SearchFilter,)
#     queryset = Customer.objects.all()
#     serializer_class = CustomerSerializer


# class CustomerDetailView(RetrieveUpdateDestroyAPIView):
#     permission_classes = [IsAdminPermission]
#     queryset = Customer.objects.all()
#     serializer_class = CustomerSerializer


