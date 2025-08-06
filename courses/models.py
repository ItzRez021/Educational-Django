from django.db import models
from accounts.models import TeacherUser,Profile
import os
import ffmpeg
import subprocess
import json
from django.db.models import Sum

class Course(models.Model):
    teacher = models.ForeignKey(TeacherUser,on_delete=models.CASCADE,related_name='course')
    students = models.ManyToManyField(Profile,blank=True,related_name='course')
    name = models.CharField(max_length=60)
    price = models.IntegerField(blank=True,null=True)
    discount = models.IntegerField(blank=True,null=True)
    total_price = models.IntegerField(default=0)
    total_hours = models.FloatField(blank=True, null=True,default=0)
    language = models.CharField(max_length=20,blank=True,null=True)
    level = models.CharField(max_length=15,blank=True,null=True)
    Sessions = models.IntegerField(default=0)
    info = models.TextField(max_length=200,blank=True,null=True)
    thumbnail = models.ImageField(upload_to='Thumbnails/',blank=True,null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    @property
    def total_income(self):
        return self.students.count()*self.total_price

    def delete(self, *args, **kwargs):
        if self.thumbnail and hasattr(self.thumbnail, 'path') and os.path.isfile(self.thumbnail.path):
            try:
                os.remove(self.thumbnail.path)
                print(f"[DELETE] Removed course thumbnail: {self.thumbnail.path}")
            except Exception as e:
                print(f"[ERROR] Couldn't delete course thumbnail: {e}")
        super().delete(*args, **kwargs)


    def save(self, *args, **kwargs):
        # Don't calculate sessions/durations until the course is saved and has a primary key
        is_new = self.pk is None
        super().save(*args, **kwargs)  # Save first to generate the pk if new

        # Now you can safely filter using self
        if not is_new:
            self.Sessions = CourseVideo.objects.filter(title__course=self).count()

            total_duration_seconds = CourseVideo.objects.filter(title__course=self).aggregate(
                Sum('duration')
            )['duration__sum'] or 0

            self.total_hours = round(total_duration_seconds / 3600, 2)

            # Price logic
            if self.price is None:
                self.total_price = 0
            elif self.discount:
                self.total_price = self.price - self.discount
            elif self.discount is None:
                self.total_price = self.price

            # Save again with updated values
            super().save(update_fields=['Sessions', 'total_hours', 'total_price'])


    def __str__(self):
        return f"{self.name}-{self.teacher.name}"



class Option(models.Model):
    mymodel = models.ForeignKey(Course, related_name='options', on_delete=models.CASCADE)
    option = models.CharField(max_length=200)

    def __str__(self):
        return self.option

class Title(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='titles')
    title = models.CharField(max_length=50)
    info = models.TextField(max_length=400,blank=True,null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.course.name}"

class CourseVideo(models.Model):
    title = models.ForeignKey(Title,on_delete=models.CASCADE,related_name='videos')
    video = models.FileField(upload_to='course-videos/',blank=True,null=True)
    thumbnail = models.ImageField(upload_to='videoes-thumbnails/',blank=True,null=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    info = models.TextField(max_length=500,blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(default=0)


    # @staticmethod
    # def get_video_duration(path):
    #     try:
    #         result = subprocess.run(
    #             ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
    #              '-of', 'default=noprint_wrappers=1:nokey=1', path],
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE,
    #             universal_newlines=True
    #         )
    #         return float(result.stdout.strip())
    #     except Exception as e:
    #         print(f"[FFPROBE subprocess error] {e}")
    #         return 0

    # def save(self, *args, **kwargs):
    #     is_new = self.pk is None

    #     super().save(*args, **kwargs)

    #     if is_new or self.duration == 0:
    #         try:
    #             video_path = self.video.path
    #             print(f"[DEBUG] Video path: {video_path}")

    #             if os.path.isfile(video_path):
    #                 print("[DEBUG] File exists, probing...")
    #                 self.duration = self.get_video_duration(video_path)
    #                 super().save(update_fields=['duration'])
    #                 print(f"[DEBUG] Duration saved: {self.duration}")
    #             else:
    #                 print("[DEBUG] File not found!")

    #         except Exception as e:
    #             print(f"[FFMPEG PROBE ERROR] {e}")

    #     self.title.course.save()

    # def delete(self, *args, **kwargs):
    #     # Store the course reference before deleting
    #     course = self.title.course

    #     # Delete the video file if it exists
    #     if self.video and hasattr(self.video, 'path') and os.path.isfile(self.video.path):
    #         try:
    #             os.remove(self.video.path)
    #             print(f"[DELETE] Removed video file: {self.video.path}")
    #         except Exception as e:
    #             print(f"[ERROR] Couldn't delete video file: {e}")

    #     # Delete the thumbnail file if it exists
    #     if self.thumbnail and hasattr(self.thumbnail, 'path') and os.path.isfile(self.thumbnail.path):
    #         try:
    #             os.remove(self.thumbnail.path)
    #             print(f"[DELETE] Removed thumbnail: {self.thumbnail.path}")
    #         except Exception as e:
    #             print(f"[ERROR] Couldn't delete thumbnail: {e}")

    #     # Delete the DB instance
    #     super().delete(*args, **kwargs)

    #     # Recalculate course stats
    #     course.save()


    def __str__(self):
        return f"{self.title.title}-{self.name}"


class Comments(models.Model):
    user = models.ForeignKey('accounts.Profile',on_delete=models.CASCADE,related_name='comment')
    vid = models.ForeignKey(CourseVideo,on_delete=models.CASCADE,related_name='comment')
    comment = models.TextField(max_length=400)
    responded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.name} - {self.vid.name}"


class RespondedComments(models.Model):
    comments = models.OneToOneField(Comments,on_delete=models.CASCADE,related_name='respond')
    teacher = models.ForeignKey(TeacherUser,on_delete=models.CASCADE,related_name='respond')
    comment = models.TextField(max_length=400)

    def __str__(self):
        return f"{self.teacher.name} - {self.comment}"