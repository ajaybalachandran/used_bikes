from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views
router = DefaultRouter()
router.register('bikes', views.BikesView, basename='bikes')
router.register('offers', views.BuyersView, basename='offers')
router.register('review_offer', views.ReviewOfferRequestsView, basename='seller')
router.register('sales', views.SalesView, basename='sales')

urlpatterns = [

]+router.urls
