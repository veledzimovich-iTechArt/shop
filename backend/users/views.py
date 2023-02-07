from rest_framework.permissions import IsAdminUser
from rest_framework import mixins
from rest_framework import viewsets

from users.serializers import AppAccountSerializer, UserSerializer
from users.models import AppAccount, User
# Create your views here.


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'head', 'options', 'post', 'patch', 'delete']


class AppAccountView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = AppAccount.objects.all()
    serializer_class = AppAccountSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'head', 'options', 'patch']
