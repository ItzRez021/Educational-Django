from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from django.urls import reverse
from django.views import View
from django.views.generic import ListView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from home.forms import NewsMateForm
from home.models import NewsMate
from django.contrib import messages
from .models import Course,Title,CourseVideo,Comments,RespondedComments
from .forms import TitleCreateForm,AddVideoForm,SignCourseForm,CommentForm,RespondCommentForm
from home.forms import NewsMateForm
from accounts.models import AfterPay,WishList,WatchedVideo,TeacherUser,Cart,CartItem

class AllCoursesView(View):
    template_name = 'courses/packages.html'
    form_class = NewsMateForm
    def get(self,request):
        Co = Course.objects.filter(status=True)
        return render(request,self.template_name,{'MU':settings.MEDIA_URL,'form':self.form_class(),'Co':Co})
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if NewsMate.objects.filter(email=data['email']).exists():
                messages.error(request,'شما قبلا عضو شده اید')
                return redirect('course:allcourses')
            else:
                new = NewsMate.objects.create(user=request.user,email=data['email'])
                new.save()
                messages.success(request,'شما به خبرنامه عضو شدید')
                return redirect('courses:allcourses')
        if form.errors:
            for field_name, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, error)

            for error in form.non_field_errors():
                messages.error(request, error)
        return render(request,self.template_name,{'form':form})

class CourseDetailView(View):
    template_name = 'courses/Educational-Product-Page.html'
    def get(self,request,*args,**kwargs):
        co = get_object_or_404(Course, pk=kwargs['pk'])

        context = {'co': co}

        if request.user.is_authenticated:
            # Check if the course is in cart
            if Cart.objects.filter(user=request.user).exists():
                ca = get_object_or_404(Cart, user=request.user)
                if ca.cartitem.filter(course=co).exists():
                    context['InCart'] = True

            # Check if the user has bought the course
            if AfterPay.objects.filter(user=request.user, course=co).exists():
                context['Out'] = True
                return render(request, self.template_name, context)

            # Check if the course is in the user's wishlist
            wishlist_exists = WishList.objects.filter(profile=request.user.profile, course=co).exists()
            if wishlist_exists:
                context['OutW'] = True
        context['MU'] = settings.MEDIA_URL
        return render(request, self.template_name, context)
    
class TeacherRemoveCourseView(LoginRequiredMixin,View):
    def post(self,request,*args,**kwargs):
        Co = get_object_or_404(Course,id=self.kwargs['id'])
        Co.delete()
        return redirect('accounts:teacherprofile', pk=request.user.teacher.pk)
    
class TeacherEditCourseView(LoginRequiredMixin,View):
    template_name = 'courses/select.html'
    def get(self,request,*args,**kwargs):
        co = get_object_or_404(Course,id=self.kwargs['id'])
        return render(request,self.template_name,{'MU':settings.MEDIA_URL,'co':co,'LayOut':True})
    
class TeacherUploadTitleView(LoginRequiredMixin,View):
    template_name = 'courses/ss-upload.html'
    form_class = TitleCreateForm
    def get(self,request,*args,**kwargs):
        co = get_object_or_404(Course,id=self.kwargs['id'])
        return render(request,self.template_name,{'MU':settings.MEDIA_URL,'co':co,'LayOut':True,'form':self.form_class()})
    def post(self,request,*args,**kwargs):
        co = get_object_or_404(Course,id=self.kwargs['id'])
        form = self.form_class(request.POST)
        if form.is_valid():
            title_co = form.save(commit=False)
            title_co.course = co
            if Title.objects.filter(course=co, title=title_co.title).exists():
                messages.error(request,'این فصل از قبل در این دوره وجود دارد')
                return redirect('courses:uploadtitle',id=co.id)
            title_co.save()
            messages.success(request,'فصل جدید با موفقیت ساخته شد')
            return redirect('courses:editcourse',id=co.id)

        if form.errors:
            for field_name, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, error)

            for error in form.non_field_errors():
                messages.error(request, error)
        return render(request,self.template_name,{'MU':settings.MEDIA_URL,'co':co,'LayOut':True,'form':form})
    
class TeacherVideoUploadView(LoginRequiredMixin,View):
    template_name = 'courses/video-upload.html'
    form_class = AddVideoForm
    def get(self,request,*args,**kwargs):
        co = get_object_or_404(Course,id=self.kwargs['id'])
        if not co.titles.all():
            messages.error(request,'دوره شما فصلی ندارد')
            return redirect('courses:editcourse',id=co.id)
        return render(request,self.template_name,{'MU':settings.MEDIA_URL,'co':co,'LayOut':True,'form':self.form_class()})

    def post(self, request,*args,**kwargs):
        co = get_object_or_404(Course, id=self.kwargs['id'])

        # Get form fields
        title_id = request.POST.get('title')
        name = request.POST.get('name')
        info = request.POST.get('info')
        video = request.FILES.get('video')
        thumbnail = request.FILES.get('thumbnail')

        # Validate title
        title_obj = Title.objects.filter(id=title_id, course=co).first()
        if not title_obj:
            messages.error(request,'دوره شما فصلی ندارد')
            return render(request, self.template_name, {
                'co': co,
                'LayOut':True
            })
        if CourseVideo.objects.filter(name=name,title__course=co).exists():
            messages.error(request,'ویدیویی با این عنوان قبلا روی این دوره بارگذاری شده است')
            return redirect('courses:uploadvideo',id=co.id)

        # Save video
        CourseVideo.objects.create(
            title=title_obj,
            name=name,
            info=info,
            video=video,
            thumbnail=thumbnail,
        )

        return redirect('courses:editcourse', id=co.id)  # change to your real URL name


class UserSignCourseView(LoginRequiredMixin,View):
    template_name = 'courses/check-payment.html'
    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated and request.user.is_teacher:
            return HttpResponse("Access Denied: You are not allowed here.")
        co = get_object_or_404(Course,pk=self.kwargs['pk'])
        if AfterPay.objects.filter(user=request.user,course=co).exists():
            return HttpResponse("Access Denied: You are not allowed here.")
        form1 = NewsMateForm()
        form2 = SignCourseForm()
        return render(request,self.template_name,{'MU':settings.MEDIA_URL,'co':co,'form1':form1,'form2':form2})
    def post(self,request,*args,**kwargs):
        co = get_object_or_404(Course,pk=self.kwargs['pk'])
        form1 = NewsMateForm()
        form2 = SignCourseForm()
        if 'submit_form1' in request.POST:
            form1 = NewsMateForm(request.POST)
            if form1.is_valid():
                data = form1.cleaned_data
                if NewsMate.objects.filter(email=data['email']).exists():
                    messages.error(request,'شما قبلا عضو شده اید')
                    return redirect('courses:signcourse',pk=self.kwargs['pk'])
                else:
                    new = NewsMate.objects.create(user=request.user,email=data['email'])
                    new.save()
                    messages.success(request,'شما به خبرنامه عضو شدید')
                    return redirect('courses:signcourse',pk=self.kwargs['pk'])
                
            if form1.errors:
                for field_name, error_list in form1.errors.items():
                    for error in error_list:
                        messages.error(request, error)

                for error in form1.non_field_errors():
                    messages.error(request, error)
            return render(request,self.template_name,{'form1':form1,'form2':form2})
        elif 'submit_form2' in request.POST:
            form2 = SignCourseForm(request.POST)
            if  AfterPay.objects.filter(user=request.user,course=co).exists():
                messages.error(request,'شما قبلا این دوره راه خریداری کرده اید')
                return redirect('accounts:profile',pk=request.user.profile.pk)
            if form2.is_valid():
                if WishList.objects.filter(profile=request.user.profile,course=co).exists():
                    w = get_object_or_404(WishList,profile=request.user.profile,course=co)
                    w.delete()
                data = form2.cleaned_data
                af = AfterPay.objects.create(user=request.user,course=co,cart=request.user.cart,name=f"{data['name']}  {data['famil']}",
                company_name=data['cn'],adress=data['adress'],country=data['country'],city=data['city'],
                postal_code=data['pc'],email=data['email'],number=data['number'],payment_info=data['paymenti'],way_to_pay=data['waytp'])
                af.save()
                co.students.add(request.user.profile)
                co.save()
                tch = co.teacher
                tch.students += 1
                tch.total_income += co.total_price
                tch.save()
                af = get_object_or_404(AfterPay,user=request.user)
                CartItem.objects.filter(cart__user=request.user, course__afterpay=af).delete()
                messages.success(request,'سفارش با موفقیت انجام شد')
                videos = CourseVideo.objects.filter(title__course=co)
                for video in videos:
                    WatchedVideo.objects.get_or_create(
                        user=request.user,
                        course=co,
                        video=video,
                        defaults={'seen': '0'}
                    )
                return redirect('accounts:profile',pk=request.user.pk)
            if form2.errors:
                for field_name, error_list in form2.errors.items():
                    for error in error_list:
                        messages.error(request, error)

                for error in form2.non_field_errors():
                    messages.error(request, error)
            return render(request,self.template_name,{'MU':settings.MEDIA_URL,'form1':form1,'form2':form2})
        return redirect('courses:signcourse', pk=self.kwargs['pk'])
    

class UserWatchCourseView(LoginRequiredMixin, View):
    template_name = 'courses/student-course.html'
    form_class = CommentForm
    def get(self, request, *args, **kwargs):
        user = request.user
        course_id = kwargs.get('id')
        video_id = kwargs.get('video_id')  # optional

        co = get_object_or_404(Course, id=course_id)

        # Permission check
        if not AfterPay.objects.filter(user=user, course=co).exists():
            messages.error(request, 'شما اجازه دسترسی به این صفحه را ندارید')
            if user.is_teacher:
                return redirect('accounts:teacherprofile', pk=user.teacher.pk)
            return redirect('accounts:profile', pk=user.pk)

        # Video selection
        all_videos = CourseVideo.objects.filter(title__course=co).order_by('title__id', 'id')
        current_video = get_object_or_404(all_videos, id=video_id) if video_id else all_videos.first()
        next_video = all_videos.filter(id__gt=current_video.id).first()
        w = WatchedVideo.objects.filter(user=user, course=co, video=current_video).first()
        if w:
            if w.seen == '0':
                w.seen = '1'
                w.save()


        context = {
            'co': co,
            'user': user,
            'MU': settings.MEDIA_URL,
            'LayOut': True,
            'current_video': current_video,
            'next_video': next_video,
            'form':self.form_class(),
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        course_id = kwargs.get('id')
        video_id = kwargs.get('video_id')

        if form.is_valid():
            course = get_object_or_404(Course, id=course_id)
            video = get_object_or_404(CourseVideo, id=video_id)
            
            # مقداردهی به فیلدهای فرم
            form.instance.user = request.user.profile
            form.instance.vid = video
            form.save()

            messages.success(request, 'کامنت شما ثبت شد')
            return redirect('courses:watch_course_video', id=course.id, video_id=video.id)
        if form.errors:
            for field_name, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, error)

            for error in form.non_field_errors():
                messages.error(request, error)
        return self.get(request, *args, **kwargs)



def UserLikeCourseView(request, *args, **kwargs):
    course = get_object_or_404(Course, id=kwargs['id'])
    
    if WishList.objects.filter(course=course,profile=request.user.profile).exists():
        w = get_object_or_404(WishList,course=course,profile=request.user.profile)
        w.delete()
    elif AfterPay.objects.filter(user=request.user,course=course).exists():
        messages.error(request,'شما دوره را خریداری کرده اید')
        return redirect('accounts:profile',pk=request.user.profile.pk)
    else:
        w = WishList.objects.create(profile=request.user.profile)
        w.course.add(course)
        w.save()
    
    return redirect('courses:coursedetail', pk=course.pk)

class TeacherCommentedToo(LoginRequiredMixin,View):
    template_name = 'accounts/teach-profile.html'
    form_class = RespondCommentForm
    def post(self,request,*args,**kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            co = get_object_or_404(Comments,id=self.kwargs['id'])
            form.instance.comments = co
            form.instance.teacher = request.user.teacher
            form.save()
            co.responded = True
            co.save()
            messages.success(request,'جواب شما ثبت شد')
            return redirect(f"{reverse('accounts:teacherprofile', kwargs={'pk': request.user.teacher.pk})}?tab=questions")
        if form.errors:
            for field_name, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, error)

            for error in form.non_field_errors():
                messages.error(request, error)
        return render(request,self.template_name,{'form':form})
    
class UserAddToCartView(LoginRequiredMixin,View):
    template_name = 'courses/Educational-Product-Page.html'
    def get(self,request, *args, **kwargs):
        if request.user.is_teacher:
            return HttpResponse('access denied')

        course = get_object_or_404(Course, pk=kwargs.get('pk'))

        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if this course is already in the cart
        if cart.cartitem.filter(course=course).exists():
            cart.cartitem.filter(course=course).delete()
            messages.success(request, 'محصول از سبد خرید شما حذف شد')
        else:
            CartItem.objects.create(cart=cart, course=course)
            messages.success(request, 'محصول به سبد خرید اضافه شد')

        return redirect('courses:coursedetail', pk=course.pk)
    
