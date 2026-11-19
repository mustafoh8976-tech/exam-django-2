from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    username = models.CharField(max_length=150,unique=True)
    email = models.CharField(max_length=150,unique=True)
    password = models.CharField(max_length=200)
    photo = models.ImageField()
    phone = models.CharField(max_length=13)
    about = models.TextField()
    
class S_Category(models.Model):
    name_c = models.CharField(max_length=150)
    count_playrs = models.IntegerField()
    
    
class Stadion(models.Model):
    name_s = models.CharField(max_length=200)
    addres = models.CharField()
    disc = models.TextField()
    category = models.ForeignKey(S_Category, on_delete=models.CASCADE)
    price = models.DecimalField()
    photo_s = models.ImageField()
    is_free = models.BooleanField(default=False)    
    
class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    stadion = models.ForeignKey(Stadion, on_delete=models.CASCADE)
    has_team = models.BooleanField(default=False)
    playrs_need = models.PositiveIntegerField()
    status = models.CharField()


class Participant(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    
    