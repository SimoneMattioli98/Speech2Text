from django import forms 
from .models import  Request

class AudioForm(forms.ModelForm):
    class Meta:
        model=Request
        fields=['record', 'record_type', 'model_choosen']

class TokenForm(forms.Form): 
    token = forms.CharField(max_length=100)