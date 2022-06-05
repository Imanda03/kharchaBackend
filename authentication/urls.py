from django.urls import path
# from rest_framework_simplejwt import views as jwt_views
from .views import (
    UserView,
    UserDetailView,
    UserListView,
    # changePassword,
    PasswordChangeAPIView,
    UserObtainTokenView, 
    # CustomerObtainTokenView,
    CustomTokenRefreshView,
    BlacklistView,
    isTokenValid,
    activateAccount,
    resetPassword,
    ForgetPasswordAPIView,
    # CustomerCRUView,
    # CustomerListView,
    # CustomerDetailView,
)

urlpatterns = [
    path('user/', UserView.as_view(), name="user"), #for EveryUser
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'), #for ADMIN
    path('user/all/', UserListView.as_view(), name="all-user"), #for ADMIN
    path('user/password/change/', PasswordChangeAPIView.as_view() , name='change-password'), 
    path('token/obtain/', UserObtainTokenView.as_view(), name='token-create'),
    # path('customer/token/obtain/', CustomerObtainTokenView.as_view(), name='token-create-customer'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('token/blacklist/', BlacklistView.as_view(), name='token-blacklist'),
    path('token/valid/', isTokenValid , name='token-valid'),
    path('user/activate/', activateAccount , name='user-activate'),
    path('user/password/reset/', resetPassword , name='user-reset'),
    path('user/password/forget/', ForgetPasswordAPIView.as_view(), name='user-forget-password'),
    # path('customer/', CustomerCRUView.as_view(), name="customer"),
    # path('customer/all/', CustomerListView.as_view(),name="all-customer"),
    # path('customer/<int:pk>/', CustomerDetailView.as_view(),name="customer-detail"),
]