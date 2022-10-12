from django.shortcuts import render
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.response import Response
from api.models import Bikes, Offer, Sales
from api.serializers import UserSerializer, BikesSerializer, BikeImageSerializer, OfferSerializer, SalesSerializer
from rest_framework import permissions
from rest_framework.decorators import action


# =========================== Users View =============================
class UsersView(ViewSet):
    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)


# =========================== Bikes View =============================
class BikesView(ModelViewSet):
    serializer_class = BikesSerializer
    queryset = Bikes.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # overriding create method because we have to sent request.user in context
    def create(self, request, *args, **kwargs):
        serializer = BikesSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)

    # overriding list method to display only posts with is_active status True
    def list(self, request, *args, **kwargs):
        all_posts = Bikes.objects.all()
        active_posts = [post for post in all_posts if post.is_active]
        serializer = BikesSerializer(active_posts, many=True)
        return Response(data=serializer.data)

    # overriding retrieve method to only retrieve the post only if it is active
    def retrieve(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        bike = Bikes.objects.get(id=id)
        if bike.is_active:
            serializer = BikesSerializer(bike)
            return Response(data=serializer.data)
        else:
            return Response({'msg': 'not found'})

    # overriding update method is because only the created user can update their own posts.
    def update(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        bike = Bikes.objects.get(id=id)
        serializer = BikesSerializer(instance=bike, data=request.data)
        if bike.user == request.user:
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data)
            else:
                return Response(data=serializer.errors)
        else:
            return Response(data='Invalid User')

    # overriding destroy method is because only the created user can delete their own posts.
    def destroy(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        bike = Bikes.objects.get(id=id)
        current_user = request.user
        if bike.user == current_user:
            bike.delete()
            return Response(data={'msg': 'deleted'})
        else:
            return Response(data='Invalid user')

    # only post created user can add images, only 4 images are allowed
    @action(methods=['POST'], detail=True)
    def add_images(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        bike = Bikes.objects.get(id=id)
        if bike.user == request.user:
            count = bike.bikeimages_set.all().count()
            if count < 4:
                serializer = BikeImageSerializer(data=request.data, context={'bike': bike})
                if serializer.is_valid():
                    serializer.save()
                    return Response(data=serializer.data)
                else:
                    return Response(data=serializer.errors)
            else:
                return Response(data={'msg': 'you can only add 4 images'})
        else:
            return Response({'msg': 'invalid user'})

    # for list all images of a specific post
    @action(methods=['GET'], detail=True)
    def get_images(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        bike = Bikes.objects.get(id=id)
        if bike.is_active:
            images = bike.bikeimages_set.all()
            serializer = BikeImageSerializer(images, many=True)
            return Response(data=serializer.data)
        else:
            return Response(data={'msg': 'not found'})

    '''---------------------Buyer can make offers here--------------------------'''
    @action(methods=['POST'], detail=True)
    def make_offer(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        bike = Bikes.objects.get(id=id)
        offers = bike.offer_set.all()
        buyer = [offer.user for offer in offers if offer.user == request.user]
        if bike.is_active and bike.user != request.user:
            if not buyer:
                serializer = OfferSerializer(data=request.data, context={'bike': bike, 'user': request.user})
                if serializer.is_valid():
                    serializer.save()
                    return Response(data=serializer.data)
                else:
                    return Response(data=serializer.errors)
            else:
                return Response(data={'msg': 'one user can make only one offer'})
        else:
            return Response(data={'msg': 'not allowed'})

    '''---------------------Seller can view offers created by buyers to their post--------------------------'''

    @action(methods=['GET'], detail=True)
    def offer_requests(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        bike = Bikes.objects.get(id=id)
        if bike.is_active:
            offers = bike.offer_set.all()
            if bike.user == request.user:
                serializer = OfferSerializer(offers, many=True)
                return Response(data=serializer.data)
            else:
                return Response(data={'msg': 'Access denied'})
        else:
            return Response(data={'msg': 'Bike not found'})

    # seller can mark their posts ad sold here
    @action(methods=['POST'], detail=True)
    def mark_as_sold(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        bike = Bikes.objects.get(id=id)
        seller = bike.user
        approved_offer = bike.offer_set.get(status='approved')
        buyer = approved_offer.user
        sale_price = approved_offer.offer_price
        remaining_offers = bike.offer_set.all().exclude(id=approved_offer.id)
        if request.user == seller:
            serializer = SalesSerializer(data=request.data,
                                         context={'bike': bike, 'seller': seller,
                                                  'buyer': buyer, 'sale_price': sale_price})
            if serializer.is_valid():
                serializer.save()
                bike.is_active = False
                bike.save()
                for ofr in remaining_offers:
                    ofr.status = 'sold-out'
                    ofr.save()
                approved_offer.status = 'you bought this product'
                approved_offer.save()
                return Response(data=serializer.data)
            else:
                return Response(data=serializer.errors)

        else:
            return Response(data='invalid user')


# =========================== Buyers View =============================
class BuyersView(ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        offers = Offer.objects.filter(user=request.user)
        serializer = OfferSerializer(offers, many=True)
        return Response(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        offer = Offer.objects.get(id=id)
        if offer.user == request.user:
            serializer = OfferSerializer(offer)
            return Response(data=serializer.data)
        else:
            return Response({'msg': 'not found'})

    def update(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        offer = Offer.objects.get(id=id)
        if offer.user == request.user and offer.bike.is_active:
            serializer = OfferSerializer(instance=offer, data=request.data)
            if serializer.is_valid():
                serializer.save()
                offer.status = 'pending'
                offer.save()
                return Response(data=serializer.data)
            else:
                return Response(data=serializer.errors)
        else:
            return Response(data={'msg': 'not allowed'})

    def delete(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        offer = Offer.objects.get(id=id)
        if offer.user == request.user:
            offer.delete()
            return Response(data={'msg': 'Deleted'})
        else:
            return Response({'msg': 'invalid user login'})


# =========================== Review Offer Requests View =============================
# this view is for seller users
class ReviewOfferRequestsView(ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        offer = Offer.objects.get(id=id)
        bike = offer.bike
        seller = offer.bike.user
        buyer = offer.user
        if seller == request.user:
            serializer = OfferSerializer(offer)
            return Response(data=serializer.data)
        else:
            return Response(data={'msg': 'invalid user login'})

    @action(methods=['POST'], detail=True)
    def accept_offer(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        offer = Offer.objects.get(id=id)
        bike = offer.bike
        remaining_offers = bike.offer_set.all().exclude(id=id)
        seller = offer.bike.user
        if request.user == seller:
            offer.status = 'approved'
            offer.save()
            for ofr in remaining_offers:
                ofr.status = 'cancelled'
                ofr.save()
            serializer = OfferSerializer(offer)
            return Response(data=serializer.data)
        else:
            return Response(data={'msg': 'invalid user'})

    @action(methods=['POST'], detail=True)
    def cancel_offer(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        offer = Offer.objects.get(id=id)
        bike_owner = offer.bike.user
        if request.user == bike_owner:
            offer.status = 'cancelled'
            offer.save()
            cancelled_offer = Offer.objects.get(id=id)
            serializer = OfferSerializer(cancelled_offer)
            return Response(data=serializer.data)
        else:
            return Response(data={'msg': 'You have no access to this functionality'})


# =========================== Sales View =============================
class SalesView(ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['GET'], detail=False)
    def sold_bikes(self, request, *args, **kwargs):
        bikes = Sales.objects.filter(seller=request.user)
        serializer = SalesSerializer(bikes, many=True)
        return Response(data=serializer.data)

    @action(methods=['GET'], detail=False)
    def bought_bikes(self, request, *args, **kwargs):
        bikes = Sales.objects.filter(buyer=request.user)
        serializer = SalesSerializer(bikes, many=True)
        return Response(data=serializer.data)