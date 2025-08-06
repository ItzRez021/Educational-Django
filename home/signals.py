import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Blog

# Utility: Safely delete a file
def delete_file_if_exists(file_field):
    if file_field and hasattr(file_field, 'path') and os.path.isfile(file_field.path):
        try:
            os.remove(file_field.path)
            print(f"[SIGNAL] Deleted file: {file_field.path}")
        except Exception as e:
            print(f"[SIGNAL ERROR] {e}")


# BLOG: delete blog icon
@receiver(post_delete, sender=Blog)
def delete_blog_icon(sender, instance, **kwargs):
    delete_file_if_exists(instance.icon)