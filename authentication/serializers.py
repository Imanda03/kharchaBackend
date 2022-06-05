from os import write
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Customer, UserToken, TOKEN_CHOICES
from rest_framework.validators import UniqueValidator
from .tasks import send_register_mail
from datetime import date
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login

from .constants import DEFAULT_ASSETS_IMAGES_PATH, ADMIN_DOMAIN, CLIENT_DOMAIN
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.conf import settings


class PasswordResetSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate(self, data):
        if validate_password(data.get("new_password1"))==None:
            if data.get("new_password1") != data.get("new_password2"):
                raise exceptions.ValidationError("New passwords are not matching.")
            return data

class PasswordChangeSerializer(PasswordResetSerializer):
    old_password = serializers.CharField(required=True)

    def validate_old_password(self, data):
        user = self.context.get("request").user
        if user.is_authenticated:
            if check_password(data, user.password)==True:
                return data
        raise exceptions.ValidationError("Old Password doesn't match.")

class TokenVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    identifier = serializers.IntegerField(required=True)
    type = serializers.ChoiceField(choices=TOKEN_CHOICES)

class MyTokenObtainSerializer(TokenObtainSerializer):

    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)
        user = self.user
        if user is not None:
            if not user.email_verified:
                raise exceptions.ValidationError("Email not verified. Please verify your email or contact us for support.")
            return {}
        raise exceptions.ValidationError("Unable to login with provided credentials")
        


class MyTokenObtainPairSerializer(MyTokenObtainSerializer):

    @classmethod
    def get_token(cls, user):
        token = RefreshToken.for_user(user)

        # Add custom claims
        token['user_id'] = user.id
        token['role'] = user.role
        token['user_email'] = user.email
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
        return data

class CustomTokenObtainSlidingSerializer(TokenRefreshSerializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])
        data = {'access': str(refresh.access_token)}
        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass
            refresh.set_jti()
            refresh.set_exp()
            data['refresh'] = str(refresh)
        return data


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToken
        exclude = ['id']

class CommonUserSerializerMixin(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(min_length=8, write_only=True)
    avatar_path = serializers.SerializerMethodField()

    def get_gender(self, obj):
        return obj.get_gender_display()

    def get_avatar_path(self, obj):
        return f"{settings.MEDIA_URL}{obj.avatar}"

class CustomUserSerializer(serializers.ModelSerializer, CommonUserSerializerMixin):
    class Meta:
        model = CustomUser
        fields = (
        'id',
        'first_name',
        'last_name',
        'date_joined',
        'is_active',
        'email',
        'password',
        'gender',
        'phone',
        'avatar',
        'last_login',
        'email_verified',
        'avatar_path',
        'role'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'last_login': {'read_only': True},
            'email_verified': {'read_only': True},
            'avatar':{'write_only':True},
            'date_joined':{'read_only':True},
            }

    

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        
        return instance

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class CustomerSerializer(serializers.ModelSerializer, CommonUserSerializerMixin):

    class Meta:
        model = Customer
        fields = (
            'id',
            'first_name',
            'last_name',
            'date_joined',
            'is_active',
            'email',
            'password',
            'gender',
            'phone',
            'avatar',
            'dob',
            'email_verified',
            'avatar_path',
            'role'
            )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'write_only': True},
            'email_verified': {'read_only': True},
            'avatar':{'write_only':True},
            'role':{'read_only':True},
            'is_active':{'read_only':True},
            'date_joined':{'read_only':True},
            # 'dob': {'required':True}
            }

    def validate_dob(self, value):
        if value is None:
            raise exceptions.ValidationError("Date of Birth is compulsary!!")
        dob = value
        today = date.today()
        if (dob.year + 7, dob.month, dob.day) > (today.year, today.month, today.day):
            raise serializers.ValidationError(
                'Must be at least 7 years old to register')
        return dob

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if validate_password(password)==None:
            instance.set_password(password)
        instance.save()
        
        return instance

    def update(self, instance, validated_data):
        if('password' in [x for x in validated_data]):
            validated_data.pop('password')
        return super().update(instance, validated_data)
