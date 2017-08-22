from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.decorators import detail_route
import rest_framework_extras

from listing.models import Listing, ListingContent, ListingPinned


class ListingSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Listing
        fields = "__all__"


class ListingCreateUpdateContentSerializer(
    serializers.HyperlinkedModelSerializer
):
    """The many-to-many with a through requires this serializer"""

    class Meta:
        model = ListingContent
        fields = ("modelbase_obj", "position")


class ListingCreateUpdatePinnedSerializer(
    serializers.HyperlinkedModelSerializer
):
    """The many-to-many with a through requires this serializer"""

    class Meta:
        model = ListingPinned
        fields = ("modelbase_obj", "position")


class ListingCreateUpdateSerializer(serializers.HyperlinkedModelSerializer):
    content = ListingCreateUpdateContentSerializer(many=True, required=False)
    pinned = ListingCreateUpdatePinnedSerializer(many=True, required=False)

    class Meta:
        model = Listing
        fields = "__all__"

    def create(self, validated_data):
        content = validated_data.pop("content", [])
        pinned = validated_data.pop("pinned", [])
        listing = super(ListingCreateUpdateSerializer, self).create(
            validated_data
        )

        for di in content:
            di["listing"] = listing
            ListingContent.objects.create(**di)

        for di in pinned:
            di["listing"] = listing
            ListingPinned.objects.create(**di)

        return listing

    def update(self, instance, validated_data):
        content = validated_data.pop("content", [])
        pinned = validated_data.pop("pinned", [])
        listing = super(ListingCreateUpdateSerializer, self).update(
            instance, validated_data
        )

        ListingContent.objects.filter(listing=listing).delete()
        for di in content:
            di["listing"] = listing
            ListingContent.objects.create(**di)

        ListingPinned.objects.filter(listing=listing).delete()
        for di in pinned:
            di["listing"] = listing
            ListingPinned.objects.create(**di)

        return listing


class ListingObjectsViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ListingCreateUpdateSerializer
        else:
            return ListingSerializer

    # Deviate from naming convention because queryset is already taken
    @detail_route(methods=["get"])
    def queryset_objects(self, request, pk, **kwargs):
        li = []
        for obj in self.get_object().queryset:
            # todo :fix this reverse
            url = "%s%s/" % (reverse("modelbase-list", request=self.request), obj.pk)
            li.append(url)
        return Response(li)

    @detail_route(methods=["get"])
    def queryset_permitted(self, request, pk, **kwargs):
        li = []
        for obj in self.get_object().queryset_permitted:
            # todo :fix this reverse
            url = "%s%s/" % (reverse("modelbase-list", request=self.request), obj.pk)
            li.append(url)
        return Response(li)


class ListingPermittedViewSet(ListingObjectsViewSet):
    queryset = Listing.permitted.all()


def register(router):
    return rest_framework_extras.register(
        router,
        (
            ("listing-listing-permitted", ListingPermittedViewSet),
            ("listing-listing", ListingObjectsViewSet)
        )
    )
