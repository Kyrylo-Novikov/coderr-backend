from rest_framework import serializers

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail


class OfferDetailCreateSerializer(serializers.ModelSerializer):
    """
    Serializes offer details for offer creating and single detail retrieval.
    """
    class Meta:
        model = OfferDetail
        fields = ['id',
                  'title',
                  'revisions',
                  'delivery_time_in_days',
                  'price',
                  'features',
                  'offer_type']


class OfferDetailUpdateSerializer(OfferDetailCreateSerializer):
    """
    Serializes offer details for updating single detail, with changed requirements.
    """
    class Meta(OfferDetailCreateSerializer.Meta):
        pass
        # extra_kwargs = {'title': {'required': False},
        #                 'revisions': {'required': False},
        #                 'delivery_time_in_days': {'required': False},
        #                 'price': {'required': False},
        #                 'features': {'required': False},
        #                 'offer_type': {'required': True}}

    def validate(self, attrs):
        if 'offer_type' not in attrs:
            raise serializers.ValidationError(
                {"offer_type": "This field is required"})
        return super().validate(attrs)


class OffersCreateSerializer(serializers.ModelSerializer):
    """
    Serializes an offer on creation, including its three nested offer details.
    """
    details = OfferDetailCreateSerializer(many=True)

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


class OfferUpdateSerializer(OffersCreateSerializer):
    """
    Serializes an offer update, including its nested offer details.
    """
    details = OfferDetailUpdateSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate_details(self, details):
        """
        Skips the exactly-3 validation so 1 to 3 details can be updated.
        """
        return details

    def update(self, instance, validated_data):
        """
        Updates the offer and its existing details, matched by offer_type.
        """
        details_data = validated_data.pop('details', None)
        instance = super().update(instance, validated_data)
        if details_data is not None:
            for detail_data in details_data:
                offer_type = detail_data.get('offer_type')
                detail_instance = instance.details.filter(
                    offer_type=offer_type).first()
                if detail_instance:
                    for attr, value in detail_data.items():
                        setattr(detail_instance, attr, value)
                    detail_instance.save()
        return instance


class OfferDetailHyperlinkSerializer(serializers.ModelSerializer):
    """
    Serializes offer detail IDs and hyperlinked URLs for list views
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='offerdetails-detail', lookup_field='id')

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']


class OfferUserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializes the public user data shown next to an offer.
    """
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username']


class OffersSingleGetSerializer(serializers.ModelSerializer):
    """
    Serializes a single offer with hyperlinked detail references and the calculated minimum price and delivery time.
    """
    user = serializers.IntegerField(source="user.id", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    details = OfferDetailHyperlinkSerializer(many=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id',
                  'user',
                  'title',
                  'image',
                  'description',
                  'created_at',
                  'updated_at',
                  'details', 'min_price', 'min_delivery_time']

    def get_min_price(self, obj):
        """
        Returns the lowest price among all details of the offer
        """
        offer_details = obj.details.all()
        return min(detail.price for detail in offer_details)

    def get_min_delivery_time(self, obj):
        """
        Returns the shortest delivery time among all details of the offer
        """
        offer_details = obj.details.all()
        return min(detail.delivery_time_in_days for detail in offer_details)


class OffersListGetSerializer(OffersSingleGetSerializer, serializers.ModelSerializer):
    """
    Serializes offer for list retrieval, including the same fields as OffersSingleGetSerializer plus user details
    """
    user_details = OfferUserDetailsSerializer(source='user', read_only=True)

    class Meta:
        model = Offer
        fields = ['id',
                  'user',
                  'title',
                  'image',
                  'description',
                  'created_at',
                  'updated_at',
                  'details', 'min_price', 'min_delivery_time', 'user_details']
