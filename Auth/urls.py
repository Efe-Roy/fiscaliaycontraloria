from .views import SignupView
from django.urls import path, include
from .views import (
    CustomAuthToken, UserListView, UserDetail, 
    get_all_team, UserProfileDetail,
    CreateOperatorView, get_all_agent, OTPVerificationView,
    RequestPasswordResetEmail, PasswordTokenCheckAPI,
    SetNewPasswordAPIView, ActivityTrackerView, CheckAuthenticatedView,
    ActivateDeactivateUser, ChangePasswordView, LogoutView
)

urlpatterns = [
    path('api/auth/authenticated', CheckAuthenticatedView.as_view()),
    path('api/rest-auth/registration/', SignupView.as_view()),
    path('api/rest-auth/login/', CustomAuthToken.as_view(), name ='auth-token'),
    path('api/userlist/', UserListView.as_view()),
    path('api/users/<int:pk>/', UserDetail.as_view()),
    path('api/rest-auth/change-password/', ChangePasswordView.as_view()),
    path('api/auth/logout', LogoutView.as_view()),

    path('api/activate-deactivate/', ActivateDeactivateUser.as_view()),

    path('api/activity-tracker/', ActivityTrackerView.as_view()),

    path('api/verify-otp/', OTPVerificationView.as_view(), name='verify-otp'),

    path('api/create-operators', CreateOperatorView.as_view()),

    path('api/user/detail/<int:pk>/', UserProfileDetail.as_view()),

    path('api/teams/', get_all_team.as_view()),
    path('api/agent/', get_all_agent.as_view()),

    path('api/request-reset-email/', RequestPasswordResetEmail.as_view(), name="request-reset-email"),
    path('api/password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('api/password-reset-complete', SetNewPasswordAPIView.as_view(), name='password-reset-complete')
]

