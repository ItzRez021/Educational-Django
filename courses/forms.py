from django import forms
from .models import Title,CourseVideo,Comments,RespondedComments
from accounts.models import AfterPay
import re

class TitleCreateForm(forms.ModelForm):
    class Meta:
        model = Title
        fields = ['title','info']

class AddVideoForm(forms.ModelForm):
    class Meta:
        model = CourseVideo
        fields = ['title','video','thumbnail','name','info']
    

class SignCourseForm(forms.Form):
    name = forms.CharField(max_length=50)
    famil = forms.CharField(max_length=50)
    cn = forms.CharField(max_length=100)
    adress = forms.CharField(max_length=300)
    country = forms.CharField(max_length=30)
    city = forms.CharField(max_length=30)
    pc = forms.CharField(max_length=20)
    email = forms.EmailField()
    number = forms.CharField(max_length=11)
    paymenti = forms.CharField(max_length=500)
    waytp = forms.CharField(max_length=10)


    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.search(r'\.(com|net|org|edu)$', email, re.IGNORECASE):
            raise forms.ValidationError("Email must end with .com, .net, .org, or .edu")
        return email
    
    def clean_number(self):
        number = self.cleaned_data['number']
        if number[0] != '0' or number[1] != '9':
            raise forms.ValidationError('شماره صحیح نیست')
        return number
    

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['comment']

class RespondCommentForm(forms.ModelForm):
    class Meta:
        model = RespondedComments
        fields = ['comment']