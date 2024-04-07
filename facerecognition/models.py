from django.db import models
from django.contrib.auth.models import User

class Photo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,default=1)
    phone_number = models.CharField(max_length=100, default='')
    address = models.CharField(max_length=100, default='')
    student_class = models.CharField(max_length=100, default='')
    image = models.ImageField(upload_to='')

    def __str__(self):
        return self.user.username



#python manage.py migrate facerecognition zero python manage.py makemigrations facerecognition python manage.py migrate