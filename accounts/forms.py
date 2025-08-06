from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User,TeacherUser
import re


class CreateUser(forms.ModelForm):
    password_1 = forms.CharField(widget=forms.PasswordInput)
    password_2 = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['email','name']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('ایمیل از قبل وجود دارد')
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
    
    def clean_password_2(self):
        data = self.cleaned_data
        if not data['password_1'] or not data['password_2']:
            raise forms.ValidationError('پسوورد نمیتواند خالی باشد')
        if len(data['password_2']) < 8:
            raise forms.ValidationError('اسم نباید از هشت کاراکتر کوچیکتر باشد')        
        if data['password_2'] != data['password_1']:
            raise forms.ValidationError('رمز ها مطابقت ندارند')
        return data['password_2']
    
    def save(self,commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password_2'])
        if commit:
            user.save()
        return user
    

class ChangeUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email','name']
        
    def clean_pass(self):
        password = ReadOnlyPasswordHashField()
        return self.initial['password']


    
class UserRegisterCodeForm(forms.Form):
    code1 = forms.IntegerField(min_value=0, max_value=9)
    code2 = forms.IntegerField(min_value=0, max_value=9)
    code3 = forms.IntegerField(min_value=0, max_value=9)
    code4 = forms.IntegerField(min_value=0, max_value=9)
    code5 = forms.IntegerField(min_value=0, max_value=9)
    code6 = forms.IntegerField(min_value=0, max_value=9)

    def clean(self):
        cleaned_data = super().clean()
        # Combine the six digits into a single string
        code_str = ''.join(str(cleaned_data.get(f'code{i}', '')) for i in range(1, 7))
        
        # Validate length and content
        if len(code_str) != 6 or not code_str.isdigit():
            raise forms.ValidationError("کد تایید باید حداقل 6 کاراکتر باشد")

        # Add combined code to cleaned_data
        cleaned_data['code'] = int(code_str)
        return cleaned_data
    

class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.search(r'\.(com|net|org|edu)$', email, re.IGNORECASE):
            raise forms.ValidationError("Email must end with .com, .net, .org, or .edu")
        return email
    
    def clean_password(self):
        data = self.cleaned_data
        if not data['password']:
            raise forms.ValidationError('پسوورد خالی است')
        if len(data['password']) < 8:
            raise forms.ValidationError('پسوورد باید حداقل هشت کاراکتر باشد')
        return data['password']


class CourseUploadForm(forms.Form):
    name = forms.CharField(max_length=60)
    info = forms.CharField(max_length=200)
    thumbnail = forms.ImageField()  # ✅ fixed spelling

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        info = cleaned_data.get('info')
        thumbnail = cleaned_data.get('thumbnail')  # ✅ fixed spelling

        if not name or not info or not thumbnail:
            raise forms.ValidationError('تمام فیلدها مورد نیاز هستند')


class UserEditEmailForm(forms.Form):
    email = forms.EmailField()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('ایمیل از قبل وجود دارد')
        if not re.search(r'\.(com|net|org|edu)$', email, re.IGNORECASE):
            raise forms.ValidationError("Email must end with .com, .net, .org, or .edu")
        return email