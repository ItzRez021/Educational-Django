from django.db import models
from accounts.models import User

class Blog(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    icon = models.ImageField(upload_to='blog/',blank=True,null=True)
    slogan = models.CharField(max_length=100,blank=True,null=True)
    first_intro = models.CharField(max_length=100,blank=True,null=True)
    introduction = models.TextField(max_length=300,blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('BlogTag', through='BlogTagRelation', related_name='blogs')
    
    def __str__(self):
        return self.user.name
    
class BlogTag(models.Model):
    tag = models.CharField(max_length=30)

    def __str__(self):
        return self.tag

class BlogTagRelation(models.Model):  # custom through table
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    tag = models.ForeignKey(BlogTag, on_delete=models.CASCADE)

    def __str__(self):
        return self.tag.tag
    
class BlogTitleInfo(models.Model):
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE)
    title = models.CharField(max_length=30,blank=True,null=True)
    info = models.TextField(max_length=500,blank=True,null=True)

    def __str__(self):
        return self.title
    
class ContactUs(models.Model):
    checked = models.BooleanField(default=False,blank=True,null=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    email = models.EmailField()
    number = models.CharField(max_length=11,blank=True,null=True)
    req_title = models.CharField(max_length=60,blank=True,null=True)
    req_pm = models.TextField(max_length=500)

    def __str__(self):
        return f"{self.name} - {self.req_title}"
    
class NewsMate(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    email = models.EmailField()

    def __str__(self):
        return self.email