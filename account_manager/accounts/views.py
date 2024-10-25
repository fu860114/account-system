from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password, make_password
from .models import User
from .serializers import UserSerializer
import uuid

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                user.token = str(uuid.uuid4())  # Generate token
                user.save()
                return Response({'token': user.token,'role':user.role,'email': user.email}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

class AccountManagementView(APIView):
    def get(self, request):
        token = request.headers.get('Authorization')
        try:
            user = User.objects.get(token=token)
            if user.role == 'Super':
                normal_users = User.objects.filter(role='Normal')
                serializer = UserSerializer(normal_users, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'error': 'Unauthorized, only Super can view the list'}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        token = request.headers.get('Authorization')
        try:
            user = User.objects.get(token=token)
            if user.role == 'Super':
                new_user = User.objects.create(
                    username=request.data['username'],
                    email=request.data['email'],
                    password=make_password(request.data['password']),
                    role='Normal'
                )
                return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_403_FORBIDDEN)


class UserView(APIView):
    def get(self, request):
        token = request.headers.get('Authorization')
        try:
            user = User.objects.get(token=token)  # 根據 token 找到使用者
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)