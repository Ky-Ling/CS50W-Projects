from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionList(models.Model):
    title = models.CharField(max_length=64)
    seller = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.IntegerField()
    image_link = models.CharField(max_length=200, blank=True, default=None, null=True)
    category = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

class Bids(models.Model):
    user = models.CharField(max_length=64)
    listingid = models.IntegerField()
    title = models.CharField(max_length=64)
    bid = models.IntegerField()

class Comment(models.Model):
    user = models.CharField(max_length=64)
    listingid = models.IntegerField()
    comment = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)


class WatchList(models.Model):
    user = models.CharField(max_length=64)
    listingid = models.IntegerField()

class Winner(models.Model):
    owner = models.CharField(max_length=64)
    winner = models.CharField(max_length=64)
    listingid=  models.IntegerField()
    winprice = models.IntegerField()
    title = models.CharField(max_length=64, null=True) 
     

