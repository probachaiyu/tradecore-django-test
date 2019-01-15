import jwt
from django.conf import settings
from django.contrib.auth import get_user_model, login, user_logged_in, authenticate
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import status, APIView
from rest_framework_jwt.settings import api_settings

from django_rest_network.permissions import IsOwner
from .serializers import CreateUserSchema, LoginUserSchema, UpdateUserSchema, UserSerializer

# Get the JWT settings
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

User = get_user_model()


class LoginView(generics.CreateAPIView):
    """
    POST auth/login/
    """

    # This permission class will over ride the global permission
    # class setting
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginUserSchema
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            # login saves the user’s ID in the session,
            # using Django’s session framework.
            login(request, user)
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            user_details = UserSerializer(user).data
            user_details['token'] = token
            user_logged_in.send(sender=user.__class__,
                                request=request, user=user)
            return Response(user_details, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

class RegisterUsersView(generics.CreateAPIView):
    """
    POST auth/register/
    """
    serializer_class = UpdateUserSchema
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = CreateUserSchema(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                    data=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                    )


class UserListView(generics.ListAPIView):
    """
    GET users/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET users/:id/
    PUT users/:id/
    DELETE songs/:id/
    """
    queryset = User.objects.all()
    serializer_class = UpdateUserSchema
    permission_classes = (IsOwner,)

    def get(self, request, *args, **kwargs):
        try:
            user = self.queryset.get(pk=kwargs["pk"])
            return Response(UpdateUserSchema(user).data)
        except User.DoesNotExist:
            return Response(
                    data={
                        "message": "User with id: {} does not exist".format(kwargs["pk"])
                        },
                    status=status.HTTP_404_NOT_FOUND
                    )

    def put(self, request, *args, **kwargs):
        try:
            user = self.queryset.get(pk=kwargs["pk"])
            serializer = UpdateUserSchema(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.update(user, serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                    data={
                        "message": "User with id: {} does not exist".format(kwargs["pk"])
                        },
                    status=status.HTTP_404_NOT_FOUND
                    )

    def delete(self, request, *args, **kwargs):
        try:
            user = self.queryset.get(pk=kwargs["pk"])
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(
                    data={
                        "message": "User with id: {} does not exist".format(kwargs["pk"])
                        },
                    status=status.HTTP_404_NOT_FOUND
                    )
