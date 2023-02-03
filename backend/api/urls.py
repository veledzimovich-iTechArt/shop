"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework import routers
from rest_framework.reverse import reverse
from rest_framework.response import Response

from units.views import ReservedUnitView, ReservedUnitsSearchView, UnitView
from shops.views import ShopView
from users.views import UserView

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from rest_framework.request import Request


router = routers.DefaultRouter()
router.register(r'units', UnitView, 'unit')
router.register(r'reserved-units', ReservedUnitView, 'reserved-unit')
router.register(
    r'reserved-search',
    ReservedUnitsSearchView,
    'reserved-search'
)
router.register(r'shops', ShopView, 'shop')
router.register(r'users', UserView, 'user')


@api_view(['GET'])
def api_auth(request: 'Request', format: str = None) -> Response:
    return Response({
        'login': reverse('admin:login', request=request, format=format),
        'logout': reverse('admin:logout', request=request, format=format)
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path(
        'api-auth/',
        include('rest_framework.urls', namespace='rest-framework')
    ),
    path('', api_auth)
]

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls'))
    ]
