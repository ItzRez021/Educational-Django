from django.contrib import admin
from .models import Course, Title, CourseVideo,Option,Comments,RespondedComments
import nested_admin

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1

class VideoInline(nested_admin.NestedTabularInline):
    model = CourseVideo
    extra = 1

class TitleInline(nested_admin.NestedTabularInline):
    model = Title
    extra = 1
    inlines = [VideoInline]

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [OptionInline,TitleInline]
    list_display = ('name', 'teacher', 'price', 'discount', 'total_hours', 'uploaded_at')
    search_fields = ('name', 'teacher__user__name')
    readonly_fields = ('total_price','total_hours','Sessions')
    list_filter = ('uploaded_at',)
    filter_horizontal = ('students',)  # for ManyToManyField
    date_hierarchy = 'uploaded_at'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'uploaded_at')
    search_fields = ('title', 'course__name')
    list_filter = ('uploaded_at',)


@admin.register(CourseVideo)
class CourseVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'video', 'uploaded_at')
    search_fields = ('title__title',)
    list_filter = ('uploaded_at',)
    readonly_fields = ('duration',)


class CommentsAdmin(admin.ModelAdmin):
    list_display = ['comment','user','vid']

class RespondedCommentsAdmin(admin.ModelAdmin):
    list_display = ['teacher','comment']

admin.site.register(RespondedComments,RespondedCommentsAdmin)
admin.site.register(Comments,CommentsAdmin)