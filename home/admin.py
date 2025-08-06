from django.contrib import admin
from .models import Blog,BlogTag,BlogTitleInfo,BlogTagRelation,ContactUs,NewsMate
from .forms import BlogTagRelationForm

# Inline for BlogTitleInfo (each blog can have multiple title/info entries)
class BlogTitleInfoInline(admin.TabularInline):
    model = BlogTitleInfo
    extra = 1


class BlogTagRelationInline(admin.TabularInline):
    model = BlogTagRelation
    form = BlogTagRelationForm  # Use custom form
    extra = 1
    fields = ['tag_name']


# Main Blog Admin
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['user', 'created', 'updated']
    inlines = [BlogTitleInfoInline, BlogTagRelationInline]
    search_fields = ['user__username']
    list_filter = ['created', 'updated']
    exclude = ['user']

    
    def save_model(self, request, obj, form, change):
        if not change:  # Only auto-set on creation
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_tags(self, obj):
        return ", ".join([tag.tag for tag in obj.tags.all()])

    get_tags.short_description = "Tags"

# BlogTag Admin (optional but useful)
@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ['tag']

# BlogTitleInfo Admin (optional)
@admin.register(BlogTitleInfo)
class BlogTitleInfoAdmin(admin.ModelAdmin):
    list_display = ['blog', 'title', 'info']

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['checked','name', 'email', 'number', 'req_title', 'user']
    search_fields = ['name', 'email', 'req_title', 'number']
    ordering = ('checked',)
    list_filter = ('checked',)

class NewsMateAdmin(admin.ModelAdmin):
    list_display = ['user','email']

admin.site.register(NewsMate,NewsMateAdmin)