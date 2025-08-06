from django.contrib import admin
from .models import User,Profile,TeacherUser,AfterPay
from django.contrib.auth.models import Group
from .forms import CreateUser,ChangeUser
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User,WishList,WatchedVideo,Cart,CartItem


class UserAdmin(BaseUserAdmin):
    form = ChangeUser
    add_form = CreateUser

    list_display = ('email', 'name', 'is_admin', 'is_teacher')
    list_filter = ('is_admin', 'is_teacher', 'is_active')
    ordering = ('email',)
    search_fields = ('email', 'name')
    
    fieldsets = (
        (None, {'fields': ('email', 'name')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_teacher')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name','password_1', 'password_2'),
        }),
    )
    filter_horizontal = ()


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name','email','is_teacher')
    search_fields = ('name','email')
    list_filter = ('email',)
    ordering = ('email',)


@admin.register(TeacherUser)
class TeacherUserAdmin(admin.ModelAdmin):
    
    list_display = ('user_email', 'user_name', 'shaba_number', 'total_income')
    search_fields = ('user__email', 'user__name', 'shaba_number')
    readonly_fields = ('total_income',)

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def user_name(self, obj):
        return obj.user.name
    user_name.short_description = 'Name'

class AfterPayAdmin(admin.ModelAdmin):
    list_display = ['user','course','name']


class WishListAdmin(admin.ModelAdmin):
    list_display = ['profile']

class WatchVAdmin(admin.ModelAdmin):
    list_display = ['user','video','seen']


admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(WatchedVideo,WatchVAdmin)
admin.site.register(WishList,WishListAdmin)
admin.site.register(User,UserAdmin)
admin.site.unregister(Group)
admin.site.register(Profile,ProfileAdmin)
admin.site.register(AfterPay,AfterPayAdmin)