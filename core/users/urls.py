from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserInfo, JWTView, ReportCreate, TelegramAuth, GetCSRF, Questions, ApiAuth, ApiLogout


urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('user/', UserInfo.as_view(), name='user_info'),
    path('report/', ReportCreate.as_view(), name='report'),
    path('question/', Questions.as_view(), name='question'),

    path('auth/telegram/', TelegramAuth.as_view(), name='telegram-auth'),

    # path('auth_telegram/', TelegramAuth.as_view(), name='auth_telegram'),
    path('auth_google/', TelegramAuth.as_view(), name='auth_google'),
    path('auth_api/', ApiAuth.as_view(), name='auth_api'),
    path('auth_logout/', ApiLogout.as_view(), name='auth_logout'),
    
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/', JWTView.as_view(), name='jwt'),
    path('csrf/', GetCSRF.as_view(), name='get_csrf'),
]
