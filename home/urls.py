from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('',views.HomePage.as_view(),name='home'),
    path('Search/',views.course_search,name='search'),
    path('ContactUs/',views.ContactUsView.as_view(),name='contactus'),
    path('ContactUs/newsmate/',views.NewsMatecontactusView.as_view(),name="contactuss"),
    path('ContactUs/rules/',views.RulesView.as_view(),name='rules'),
    path('ContactUs/privacy/',views.PrivacyView.as_view(),name='privacy'),
    path('blog/',views.BlogView.as_view(),name='blog'),
    path('blogpost/<int:pk>/',views.BlogPostView.as_view(),name='blogpost'),
]