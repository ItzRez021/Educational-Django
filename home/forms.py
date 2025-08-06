from django import forms
from .models import BlogTagRelation, BlogTag,NewsMate,ContactUs
import re

class BlogTagRelationForm(forms.ModelForm):
    tag_name = forms.CharField(max_length=30, label="Tag")

    class Meta:
        model = BlogTagRelation
        fields = []  # چون داریم همه چیز رو دستی مدیریت می‌کنیم

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # مقدار اولیه رشته تگ رو بذار
        if self.instance and self.instance.pk and self.instance.tag:
            self.fields['tag_name'].initial = self.instance.tag.tag

    def clean_tag_name(self):
        tag_name = self.cleaned_data['tag_name'].strip()
        tag_obj, created = BlogTag.objects.get_or_create(tag=tag_name)
        return tag_obj

    def save(self, commit=True):
        tag_obj = self.cleaned_data['tag_name']
        self.instance.tag = tag_obj
        return super().save(commit=commit)


class ContactUsForm(forms.Form):
    name = forms.CharField(max_length=60)
    email = forms.EmailField(widget=forms.EmailInput)
    number = forms.CharField(max_length=11)
    req_title = forms.CharField(max_length=60)
    req_pm = forms.CharField(max_length=500,min_length=50)
    check = forms.BooleanField(required=True,widget=forms.CheckboxInput)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.search(r'\.(com|net|org|edu)$', email, re.IGNORECASE):
            raise forms.ValidationError("Email must end with .com, .net, .org, or .edu")
        return email
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 8:
            raise forms.ValidationError('اسم نباید از هشت کاراکتر کوچیکتر باشد')
        if name[0].isdigit():
            raise forms.ValidationError('اسم نمیتواند با عدد شروع شود')
        return name
    
    def clean_number(self):
        number = str(self.cleaned_data.get('number'))
        if number[1] != "9" or number[0] != "0":
            raise forms.ValidationError('شماره تلفن درست نیست')
        return number
    
class ContactUsHomeForm(forms.Form):
    name = forms.CharField(max_length=60)
    email = forms.EmailField(widget=forms.EmailInput)
    req_pm = forms.CharField(max_length=500,min_length=50)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.search(r'\.(com|net|org|edu)$', email, re.IGNORECASE):
            raise forms.ValidationError("Email must end with .com, .net, .org, or .edu")
        return email
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 8:
            raise forms.ValidationError('اسم نباید از هشت کاراکتر کوچیکتر باشد')
        if name[0].isdigit():
            raise forms.ValidationError('اسم نمیتواند با عدد شروع شود')
        return name
    
class IndexContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['name','email','req_pm']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.search(r'\.(com|net|org|edu)$', email, re.IGNORECASE):
            raise forms.ValidationError("Email must end with .com, .net, .org, or .edu")
        return email
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 8:
            raise forms.ValidationError('اسم نباید از هشت کاراکتر کوچیکتر باشد')
        if name[0].isdigit():
            raise forms.ValidationError('اسم نمیتواند با عدد شروع شود')
        return name


class NewsMateForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = NewsMate
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.search(r'\.(com|net|org|edu)$', email, re.IGNORECASE):
            raise forms.ValidationError("Email must end with .com, .net, .org, or .edu")
        return email