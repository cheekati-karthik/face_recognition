from django import forms
from multiupload.fields import MultiFileField
from .models import Photo,StudentDetail

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = []
    
    images = MultiFileField(min_num=1, max_num=10, max_file_size=1024*1024*5) 
    
class StudentForm(forms.ModelForm):
    class Meta:
        model = StudentDetail
        fields = ['Class','department','phone_number','address']
        
    def __init__(self,*args,**kwargs):
        super(StudentForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'