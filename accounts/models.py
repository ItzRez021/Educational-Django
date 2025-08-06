from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self,name,email,password):
        if not name:
            raise ValueError('Name Field Is Empty')
        if not email:
            raise ValueError('Email Field Is Empty')
        user = self.model(name=name,email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,name,email,password):
        user = self.create_user(name,email,password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    name = models.CharField(max_length=60)
    email = models.EmailField(unique=True)
    is_teacher = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self,perm,obj=None):
        return True
    
    def has_module_perms(self,app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin
    
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    name = models.CharField(max_length=60)
    email = models.EmailField(unique=True)
    is_teacher = models.BooleanField(default=False)
    icon = models.ImageField(upload_to='accounts_profiles/',default='accounts_profiles/def.png',blank=True,null=True)
    signed_courses = models.IntegerField(default=0)
    ended_courses = models.IntegerField(default=0)
    documents = models.IntegerField(default=0)


    def __str__(self):
        return self.user.email
    

class TeacherUser(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='teacher')
    name = models.CharField(max_length=60,blank=True,null=True)
    email = models.EmailField(unique=True,blank=True,null=True)
    icon = models.ImageField(upload_to='teachers_profile/',default='teachers_profile/tch.png')
    bio = models.TextField(max_length=250,blank=True,null=True)
    number = models.CharField(max_length=11,blank=True,null=True)
    linkdin_link = models.CharField(max_length=100,blank=True,null=True)
    github_link = models.CharField(max_length=100,blank=True,null=True)
    private_site = models.CharField(max_length=100,blank=True,null=True)
    shaba_number = models.CharField(max_length=24,blank=True,null=True)
    total_income = models.IntegerField(default=0)
    students = models.IntegerField(default=0)

    def __str__(self):
        return f"Teacher: {self.user.name} ({self.user.email})"

    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.name:
                self.name = self.user.name
            if not self.email:
                self.email = self.user.email
        super().save(*args, **kwargs)


class AfterPay(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='afterpay')
    course = models.ForeignKey('courses.Course',on_delete=models.CASCADE,related_name='afterpay')
    cart = models.OneToOneField('accounts.Cart',on_delete=models.CASCADE,related_name='afterpay',blank=True,null=True)
    name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    adress = models.CharField(max_length=300)
    country = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    postal_code = models.CharField(max_length=20)
    email = models.EmailField()
    number = models.CharField(max_length=11)
    payment_info = models.TextField(max_length=500)
    PAYMENT_METHOD = [('paypal','PayPal'),('direct','Direct'),]
    way_to_pay = models.CharField(max_length=10,choices=PAYMENT_METHOD,default='direct')


    def __str__(self):
        return f"{self.name}-{self.course.name}"
    

class WishList(models.Model):
    profile = models.OneToOneField(Profile,on_delete=models.CASCADE,related_name='wishlist')
    course = models.ManyToManyField('courses.Course')


class WatchedVideo(models.Model):
    class Meta:
        unique_together = ('user', 'course', 'video')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course',on_delete=models.CASCADE,related_name='watched')
    video = models.ForeignKey('courses.CourseVideo', on_delete=models.CASCADE)
    choice_ha = [('1','1'),('0','0'),]
    seen = models.CharField(max_length=1,choices=choice_ha,blank=True,null=True,default='0')
    watched_at = models.DateTimeField(auto_now_add=True)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_prices(self):
        return sum(item.course.total_price for item in self.cartitem.all())

    @property
    def total_discount(self):
        return sum((item.course.discount or 0) for item in self.cartitem.all())

    @property
    def total_base_price(self):
        return sum((item.course.price or 0) for item in self.cartitem.all())

    def __str__(self):
        return str(self.user)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cartitem')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='cartitem')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cart.user.username} - {self.course.name}"
