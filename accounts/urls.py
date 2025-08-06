from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/',views.UserRegisterView.as_view(),name='register'),
    path('register/code/', views.VerifyCodeView.as_view(), {'mode': 'register'}, name='registercode'),
    path('login/',views.UserLoginView.as_view(),name='login'),
    path('profile/<int:pk>/',views.UserProfileView.as_view(),name='profile'),
    path('userchangeprofile/<int:pk>/',views.UserChangeProfileView.as_view(),name='userchangeprof'),
    path('logout/',views.UserLogoutView.as_view(),name='logout'),
    path('teacherprofile/<int:pk>/',views.TeacherProfileView.as_view(),name='teacherprofile'),
    path('changepassword/',views.UserChangePasswordView.as_view(),name='changepass'),
    path('TeacherChangeProfile/',views.TeacherChangeProfileView.as_view(),name='teacherchangeprofile'),
    path('TeacherUploadCourse/',views.TeacherCourseUploadView.as_view(),name='courseupload'),
    path('userchangeemail/',views.UserChangeEmailView.as_view(),name='changeemail'),
    path('userchangeemail/code/', views.VerifyCodeView.as_view(), {'mode': 'changeemail'}, name='changeemailcode'),
    path('teacherprofile/<int:pk>/questions/',views.TeacherQuestionsView.as_view(), name='teacher_questions'),
    path('UserCart/<int:pk>/',views.UserCartView.as_view(),name='cart'),
]