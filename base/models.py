from email.policy import default
from django.db import models
#from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractUser

# null=True --> This for database can be null
# blank=True --> This for form displayed on html can be blank (Client no need to fill to submit form)
# auto_now --> means it will update timestamp every time you change value in each attribute
# auto_now_add --> means it will update timestamp for the first time you add a value
# on_delete=models.SET_NULL --> This means when id in Room was deleted, the room in Message is still remaining
# on_delete=models.CASCADE --> This means when id in Room was deleted, the room in Message will be deleted also

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True,null=True)
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True, default="avatar.svg")
    USERNAME_FIELD =  'email'
    REQUIRED_FIELDS = []

#Create your models here.
class Topic(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self) -> str:
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description =  models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-updated', '-created']
    
    # To return class object as string --> example self.name
    def __str__(self) -> str:
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-updated', '-created']
        
    def __str__(self) -> str:
        return self.body[0:50] #Preview only 50 characters