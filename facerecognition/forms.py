from django import forms
from multiupload.fields import MultiFileField
from .models import Photo

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['roll_number','first_name','last_name','student_class']
    
    images = MultiFileField(min_num=1, max_num=10, max_file_size=1024*1024*5) 
    