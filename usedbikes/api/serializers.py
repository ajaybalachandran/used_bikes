from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import Bikes, BikeImages, Offer, Sales


class UserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class BikeImageSerializer(serializers.ModelSerializer):
    bike = serializers.CharField(read_only=True)

    class Meta:
        model = BikeImages
        fields = ['bike', 'image']

    def create(self, validated_data):
        bike = self.context.get('bike')
        return BikeImages.objects.create(**validated_data, bike=bike)


class BikesSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    user = serializers.CharField(read_only=True)
    # get_images field is method name from Bikes model
    get_images = BikeImageSerializer(many=True, read_only=True)
    is_active = serializers.CharField(read_only=True)

    class Meta:
        model = Bikes
        fields = '__all__'

    def create(self, validated_data):
        user = self.context.get('user')
        return Bikes.objects.create(**validated_data, user=user)


class OfferSerializer(serializers.ModelSerializer):
    bike = serializers.CharField(read_only=True)
    user = serializers.CharField(read_only=True)

    class Meta:
        model = Offer
        fields = '__all__'

    def create(self, validated_data):
        bike = self.context.get('bike')
        user = self.context.get('user')
        return Offer.objects.create(**validated_data, bike=bike, user=user)


class SalesSerializer(serializers.ModelSerializer):
    bike = serializers.CharField(read_only=True)
    seller = serializers.CharField(read_only=True)
    buyer = serializers.CharField(read_only=True)
    sale_price = serializers.CharField(read_only=True)
    sale_date = serializers.CharField(read_only=True)

    class Meta:
        model = Sales
        fields = '__all__'

    def create(self, validated_data):
        bike = self.context.get('bike')
        seller = self.context.get('seller')
        buyer = self.context.get('buyer')
        sale_price = self.context.get('sale_price')
        return Sales.objects.create(**validated_data, bike=bike, seller=seller, buyer=buyer, sale_price=sale_price)


