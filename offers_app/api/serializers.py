from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializes offer details for offer creating and single detail retrieval.
    """
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days',
                  'price', 'features', 'offer_type']


class OffersCreateSerializer(serializers.ModelSerializer):
    """
    Serializes an offer upon creation, icluding its nested offer details.
    """
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate_details(self, details):
        """
        Validates that an offer contain 3 items.
        """
        if len(details) != 3:
            raise serializers.ValidationError(
                "An offer must contain 3 details.")
        return details

    def create(self, validated_data):
        """
        Create the Offer instance with its OfferDetail objects.
        """
        details_list = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_list:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer


class OfferDetailHyperlinkSerializer(serializers.ModelSerializer):
    """
    Serializes offer detail IDs and hyperlinked URLs for list views
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='offerdetails-detail', lookup_field='id')

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']


class OffersGetSerializer(serializers.ModelSerializer):
    """
    Serializes offer for list retrieval, including hyperlinked detail refernces    """
    user = serializers.IntegerField(source="user.id", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    details = OfferDetailHyperlinkSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id',
                  'user',
                  'title',
                  'image',
                  'description',
                  'created_at',
                  'updated_at',
                  'details']
