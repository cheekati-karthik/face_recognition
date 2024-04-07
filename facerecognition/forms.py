from django import forms
from multiupload.fields import MultiFileField
from .models import Photo

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['phone_number','address','student_class']
    
    images = MultiFileField(min_num=1, max_num=10, max_file_size=1024*1024*5) 
    