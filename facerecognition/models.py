from django.contrib.auth.models import User
from django.db import models

class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='')

    def __str__(self):
        return self.user.username



#python manage.py migrate facerecognition zero python manage.py makemigrations facerecognition python manage.py migrate