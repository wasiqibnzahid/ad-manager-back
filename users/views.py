from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import BasePermission

User = get_user_model()

# Custom permission for admin-only access


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff

# Login view to get JWT token


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                "user": {
                    'username': user.username,  # Include username in response
                    'is_admin': user.is_staff or user.is_superuser,  # Include is_admin boolean
                    "report_id": user.report_id
                }

            })
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# Admin-only route to create non-admin users


class AdminCreateUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        report_id = request.data.get('report_id')

        if not username or not password:
            return Response({"detail": "Missing username or password"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a non-admin user
        user = User.objects.create_user(
            username=username, password=password, report_id=report_id)
        return Response({"detail": f"User {username} created successfully"}, status=status.HTTP_201_CREATED)

# User protected route


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "user": {
                'username': user.username,  # Include username in response
                'is_admin': user.is_staff or user.is_superuser,  # Include is_admin boolean
                "report_id": user.report_id
            }
        })
