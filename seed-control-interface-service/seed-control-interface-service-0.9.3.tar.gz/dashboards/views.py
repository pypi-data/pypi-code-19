from .models import UserDashboard, Dashboard, Definition
from rest_framework import filters, viewsets, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import (UserDashboardSerializer, DashboardSerializer,
                          DefinitionSerializer)


class DashboardViewSet(viewsets.ReadOnlyModelViewSet):

    """
    API endpoint that allows dashboard to be viewed
    """
    permission_classes = (IsAuthenticated,)
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer


class UserDashboardViewSet(viewsets.ReadOnlyModelViewSet):

    """
    API endpoint that allows user dashboard to be viewed
    """
    permission_classes = (IsAuthenticated,)
    queryset = UserDashboard.objects.all()
    serializer_class = UserDashboardSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filter_fields = ('user_id', )


class DefinitionViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):

    """
    API endpoint that allows definition to be created
    retrieved, updated and deleted
    """
    permission_classes = (IsAuthenticated,)
    queryset = Definition.objects.all()
    serializer_class = DefinitionSerializer
