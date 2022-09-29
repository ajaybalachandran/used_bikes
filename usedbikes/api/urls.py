from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views
router = DefaultRouter()
router.register('bikes', views.BikesView, basename='bikes')
router.register('offers', views.OffersView, basename='offers')

urlpatterns = [

]+router.urls
