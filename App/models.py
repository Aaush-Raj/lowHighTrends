from django.db import models

# Create your models here.
# models.py

class SignUp(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.email
