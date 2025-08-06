from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CourseVideo,Course
import os

@receiver([post_save, post_delete], sender=CourseVideo)
def update_course_sessions(sender, instance, **kwargs):
    course = instance.title.course
    session_count = CourseVideo.objects.filter(title__course=course).count()
    course.Sessions = session_count
    course.save(update_fields=['Sessions'])


@receiver(post_delete, sender=CourseVideo)
def delete_coursevideo_files(sender, instance, **kwargs):
    if instance.video and hasattr(instance.video, 'path') and os.path.isfile(instance.video.path):
        try:
            os.remove(instance.video.path)
            print(f"[SIGNAL] Deleted video: {instance.video.path}")
        except Exception as e:
            print(f"[SIGNAL ERROR] Video: {e}")

    if instance.thumbnail and hasattr(instance.thumbnail, 'path') and os.path.isfile(instance.thumbnail.path):
        try:
            os.remove(instance.thumbnail.path)
            print(f"[SIGNAL] Deleted thumbnail: {instance.thumbnail.path}")
        except Exception as e:
            print(f"[SIGNAL ERROR] Thumbnail: {e}")

    # Re-save the course to update total_hours
    if instance.title and instance.title.course:
        instance.title.course.save()


@receiver(post_delete, sender=Course)
def delete_course_thumbnail(sender, instance, **kwargs):
    if instance.thumbnail and hasattr(instance.thumbnail, 'path') and os.path.isfile(instance.thumbnail.path):
        try:
            os.remove(instance.thumbnail.path)
            print(f"[SIGNAL] Deleted course thumbnail: {instance.thumbnail.path}")
        except Exception as e:
            print(f"[SIGNAL ERROR] Course thumbnail: {e}")