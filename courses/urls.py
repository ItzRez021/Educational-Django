from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('courses/',views.AllCoursesView.as_view(),name='allcourses'),
    path('coursedetail/<int:pk>/',views.CourseDetailView.as_view(),name='coursedetail'),
    path('RemoveCourse/<int:id>/',views.TeacherRemoveCourseView.as_view(),name='removecourse'),
    path('EditCourse/<int:id>/',views.TeacherEditCourseView.as_view(),name='editcourse'),
    path('EditCourse/uploadtitle/<int:id>/',views.TeacherUploadTitleView.as_view(),name='uploadtitle'),
    path('EditCourse/uploadvideo/<int:id>/',views.TeacherVideoUploadView.as_view(),name='uploadvideo'),
    path('usersigncourse/<int:pk>/',views.UserSignCourseView.as_view(),name='signcourse'),
    path('AddTocart/<int:pk>/',views.UserAddToCartView.as_view(),name='addtocartcourse'),
    path('WatchTheCourse/<int:id>/',views.UserWatchCourseView.as_view(),name='watchthecourse'),
    path('WatchTheCourse/<int:id>/<int:video_id>/',views.UserWatchCourseView.as_view(), name='watch_course_video'),
    path('userlikecourse/<int:id>/',views.UserLikeCourseView,name='uprate'),
    path('teacherrespondtocomment/<int:id>/',views.TeacherCommentedToo.as_view(),name='teacherrespond'),
]