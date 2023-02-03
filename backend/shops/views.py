from rest_framework import mixins
from rest_framework import permissions
from rest_framework import viewsets
from shops.models import Shop
from shops.serializers import ShopSerializer

# Create your views here.


class ShopView(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()
