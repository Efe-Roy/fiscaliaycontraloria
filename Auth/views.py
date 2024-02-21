import random
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

class CheckAuthenticatedView(APIView):
    def get(self, request, format=None):
        user = self.request.user

        try:
            isAuthenticated = user.is_authenticated

            if isAuthenticated:
                return Response({ 'isAuthenticated': 'success' })
            else:
                return Response({ 'isAuthenticated': 'error' })
        except:
            return Response({ 'error': 'Something went wrong when checking authentication status' })

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        user= serializer.validated_data['user']

        if not user.is_active:
            return Response({'message': 'Account is not active.'}, status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "token":token.key,
            "is_vendor": user.is_vendor
        })

class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'PageSize'

class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = User.objects.filter(is_staff=False).order_by('-date_joined')

        # Filter based on request parameters
        username = self.request.query_params.get('username', None)
        if username:
            queryset = queryset.filter(username__icontains=username)

        is_active = self.request.query_params.get('is_active', False)
        if is_active:
            queryset = queryset.filter(is_active=is_active)

        is_vendor = self.request.query_params.get('is_vendor', False)
        if is_vendor:
            queryset = queryset.filter(is_vendor=is_vendor)
   
        return queryset


class UserDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        # current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        # Check if the current password is correct
        # if not user.check_password(current_password):
        #     return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password and save the user
        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password successfully changed.'}, status=status.HTTP_200_OK)
    
class LogoutView(APIView):
    def post(self, request, format=None):
        try:
            # auth.logout(request)
            request.auth.delete()
            return Response({ 'success': 'Loggout Out' })
        except:
            return Response({ 'error': 'Something went wrong when logging out' })
        
class DeleteAccountView(APIView):
    def delete(self, request, format=None):
        user = self.request.user

        try:
            User.objects.filter(id=user.id).delete()

            return Response({ 'success': 'User deleted successfully' })
        except:
            return Response({ 'error': 'Something went wrong when trying to delete user' })
