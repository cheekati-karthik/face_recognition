from django.db import models

class Photo(models.Model):
    roll_number = models.CharField(max_length=100,default="")
    first_name = models.CharField(max_length=100,default='')
    last_name = models.CharField(max_length=100,default='')
    student_class = models.CharField(max_length=100,default='')
    image = models.ImageField(upload_to='')



#python manage.py migrate facerecognition zero python manage.py makemigrations facerecognition python manage.py migrate