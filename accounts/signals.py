from django.db.models.signals import post_save,pre_save,m2m_changed,post_delete
from django.dispatch import receiver
from .models import User, Profile,TeacherUser,Cart

from courses.models import Course
import os

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            email=instance.email,
            is_teacher=instance.is_teacher,
            name=instance.name,
        )
    else:
        try:
            profile = instance.profile
        except Profile.DoesNotExist:
            Profile.objects.create(
                user=instance,
                email=instance.email,
                is_teacher=instance.is_teacher,
                name=instance.name,
            )
            return

        updated = False
        if profile.email != instance.email:
            profile.email = instance.email
            updated = True
        if profile.is_teacher != instance.is_teacher:
            profile.is_teacher = instance.is_teacher
            updated = True
        if profile.name != instance.name:
            profile.name = instance.name
            updated = True
        if updated:
            profile.save(update_fields=['email', 'is_teacher', 'name'])


@receiver(post_save, sender=Profile)
def update_user_from_profile(sender, instance, **kwargs):
    user = instance.user
    updated = False
    if user.email != instance.email:
        user.email = instance.email
        updated = True
    if user.is_teacher != instance.is_teacher:
        user.is_teacher = instance.is_teacher
        updated = True
    if user.name != instance.name:
        user.name = instance.name
        updated = True
    if updated:
        user.save(update_fields=['email', 'is_teacher', 'name'])


@receiver(post_save, sender=User)
def create_teacher_profile(sender, instance, created, **kwargs):
    if instance.is_teacher:
        # Create TeacherUser only if it doesn't exist
        TeacherUser.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def manage_teacher_profile(sender, instance, created, **kwargs):
    if instance.is_teacher:
        # If user is a teacher and doesn't have a TeacherUser, create it
        TeacherUser.objects.get_or_create(user=instance)
    else:
        # If user is not a teacher but has a TeacherUser profile, delete it
        TeacherUser.objects.filter(user=instance).delete()


@receiver(pre_save, sender=TeacherUser)
def sync_teacheruser_with_user(sender, instance, **kwargs):
    user = instance.user

    updated = False

    # Only update if values actually differ
    if instance.name and instance.name != user.name:
        user.name = instance.name
        updated = True

    if instance.email and instance.email != user.email:
        user.email = instance.email
        updated = True

    # Save user only if something changed
    if updated:
        user.save(update_fields=['name', 'email'])

# Utility: Safely delete a file
def delete_file_if_exists(file_field):
    if file_field and hasattr(file_field, 'path') and os.path.isfile(file_field.path):
        try:
            os.remove(file_field.path)
            print(f"[SIGNAL] Deleted file: {file_field.path}")
        except Exception as e:
            print(f"[SIGNAL ERROR] {e}")

# PROFILE: delete icon
@receiver(post_delete, sender=Profile)
def delete_profile_icon(sender, instance, **kwargs):
    if instance.icon.name != 'accounts_profiles/def.png':  # Avoid deleting default icon
        delete_file_if_exists(instance.icon)

# TEACHER: delete icon
@receiver(post_delete, sender=TeacherUser)
def delete_teacher_icon(sender, instance, **kwargs):
    if instance.icon.name != 'teachers_profile/tch.png':  # Avoid deleting default icon
        delete_file_if_exists(instance.icon)


@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)