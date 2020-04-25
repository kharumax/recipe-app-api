from rest_framework import generics,authentication,permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import UserSerializer,AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,) # この処理を満たすユーザーのみ通す
    permission_classes = (permissions.IsAuthenticated,) # 上と同じ,

    def get_object(self):
        """Retrieve and return auth user"""
        return self.request.user



