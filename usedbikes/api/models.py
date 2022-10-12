from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Bikes(models.Model):
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=50)
    km_driven = models.CharField(max_length=50)
    price = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    # method for get all images of specific bike object. go and look in BikeSerializer for next step
    def get_images(self):
        return self.bikeimages_set.all()

    def __str__(self):
        return self.model


class BikeImages(models.Model):
    bike = models.ForeignKey(Bikes, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='bike-images', null=True)


class Offer(models.Model):
    bike = models.ForeignKey(Bikes, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    offer_price = models.PositiveIntegerField()
    options = (
        ('cancelled', 'cancelled'),
        ('approved', 'approved'),
        ('pending', 'pending'),
        ('sold-out', 'sold-out'),
        ('you bought this product', 'you bought this product')
    )
    status = models.CharField(max_length=120, choices=options, default='pending')

    def __str__(self):
        return str(self.offer_price)


class Sales(models.Model):
    # bike = models.ForeignKey(Bikes, on_delete=models.DO_NOTHING)
    bike = models.OneToOneField(Bikes, on_delete=models.DO_NOTHING)
    seller = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='s_user')
    buyer = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='b_user')
    # sale_price = models.ForeignKey(Offer, on_delete=models.DO_NOTHING)
    sale_price = models.PositiveIntegerField()
    sale_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.bike.model
