from django.contrib.auth.models import User
from django.db import models


CLASS_CHOICES = (
    ('I','I'),
    ('II', 'II'),
    ('III','III'),
    ('IV','IV'),
)

DEPARTMENT_CHOICES = (
    ('AI/ML','AI/ML'),
    ('DS','DS'),
    ('CSE', 'CSE'),
    ('ECE','ECE'),
    ('MECH','MECH'),
    ('CIVIL','CIVIL'),
)

class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='')
    
    def __str__(self):
        return self.user.username


class StudentDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Class = models.CharField(max_length=6, choices=CLASS_CHOICES, default='I')
    department = models.CharField(max_length=6, choices=DEPARTMENT_CHOICES, default='CSE')
    phone_number=models.CharField(max_length=11,default='')
    address=models.CharField(max_length=100,default='')
  
class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date=models.DateField()
    time_in=models.TimeField()
    time_out=models.TimeField(default='None')
    Camera_id=models.CharField(max_length=20,default="00:00")
    
    def __str__(self):
        return self.user.username




#python manage.py migrate facerecognition zero python manage.py makemigrations facerecognition python manage.py migrate