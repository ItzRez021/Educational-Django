from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from django.urls import reverse,reverse_lazy
from .forms import CreateUser,UserRegisterCodeForm,UserLoginForm,CourseUploadForm,UserEditEmailForm
from .models import User,Profile,TeacherUser
from django.contrib import messages
from django.contrib.auth import login, views as auth_view,authenticate
from django.core.mail import EmailMessage,EmailMultiAlternatives
from random import randint
from django.conf import settings
from django.views import View
from django.views.generic import ListView,DetailView,UpdateView,TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from courses.models import Course,Title,CourseVideo,Comments,RespondedComments
from accounts.models import AfterPay,WishList,WatchedVideo,Cart,CartItem

class UserRegisterView(View):
    template_name = 'accounts/register.html'
    form_class = CreateUser
    def get(self,request,*args,**kwargs):
        return render(request,self.template_name,{'form':self.form_class(),'MU':settings.MEDIA_URL})
    def post(self,request,*args,**kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            random_code = randint(100000, 999999)
            request.session['register_data'] = form.cleaned_data
            request.session['register_code'] = random_code
            subject = 'Activation Code'
            from_email = 'طراحان OFFSITE <rz1125.1386@gmail.com>'
            to_email = [data['email']]

            # Plain text version (fallback for email clients that don't support HTML)
            text_content = (
                f"{data['name']}،کاربر گرامی\n"
                f"{random_code}:کد شما\n"
            )

            # HTML version with simple styling
            html_content = f"""
            <html lang="fa" dir="rtl">
            <head>
                <style>
                body {{
                    font-family: 'Tahoma', sans-serif;
                    background-color: #f9f9f9;
                    color: #333;
                    padding: 20px;
                }}
                .container {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    max-width: 600px;
                    margin: auto;
                }}
                h1 {{
                    color: #4CAF50;
                }}
                .code {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #e91e63;
                    margin-top: 20px;
                }}
                p {{
                    line-height: 1.6;
                    font-size: 16px;
                }}
                </style>
            </head>
            <body>
                <div class="container">
                <h1>کاربر گرامی، {data['name']}</h1>
                <p>کد شما:</p>
                <p class="code">{random_code}</p>
                </div>
            </body>
            </html>
            """
            email = EmailMultiAlternatives(
                subject,
                text_content,
                from_email,
                to_email,
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            request.session['allow'] = True
            return redirect('accounts:registercode')
        if form.errors:
            for field_name, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, error)

            for error in form.non_field_errors():
                messages.error(request, error)

        return render(request,self.template_name,{'form':form,'MU':settings.MEDIA_URL})

# class UserChangeEmailCodeView(LoginRequiredMixin, View):
#     form_class = UserRegisterCodeForm
#     template_name = 'accounts/verify-code.html'\

#     def get(self, request, *args, **kwargs):
#         if self.request.user.is_teacher == True:
#             return HttpResponse("Access Denied: You are not allowed here.")
#         return render(request, self.template_name, {
#             'form': self.form_class(),
#             'LayOut': True
#         })

#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             session_email = request.session.get('emailchange_data')
#             session_code = request.session.get('emailchange_code')

#             if not session_email or not session_code:
#                 messages.error(request, 'Session expired. Please try again.')
#                 return redirect('accounts:changeemail')

#             if int(form.cleaned_data['code']) == int(session_code):
#                 request.user.email = session_email
#                 request.user.save()
#                 messages.success(request, 'Email successfully changed.')

#                 # Clean session
#                 request.session.pop('emailchange_data', None)
#                 request.session.pop('emailchange_code', None)
#                 if request.user.is_teacher:
#                     return redirect('accounts:profile', pk=request.user.pk)
#                 else:
#                     return redirect('accounts:teacherprofile', pk=request.user.pk)
#             else:
#                 messages.error(request, 'Incorrect code.')

#         return render(request, self.template_name, {
#             'form': form,
#             'LayOut': True
#         })


# class UserRegisterCodeView(View):
#     template_name = 'accounts/verify-code.html'
#     form_class = UserRegisterCodeForm
#     def get(self,request,*args,**kwargs):
#         return render(request,self.template_name,{'form':self.form_class()})
#     def post(self,request,*args,**kwargs):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             data = request.session.get('register_data')
#             code = request.session.get('register_code')
#             if not data or not code:
#                 messages.error(request,'session expired')
#                 return redirect('accounts:register')
#             if int(code) == form.cleaned_data['code']:
#                 user = User.objects.create_user(email=data['email'],name=data['name'],
#                                                 password=data['password_2'])
#                 user.save()
#                 login(request,user)
#                 messages.success(request,'signed in successfuly')
#                 request.session.pop('register_data', None)
#                 request.session.pop('register_code', None)
#                 return redirect('home:home')
#             else:
#                 messages.error(request,'کد تایید اشتباه است')

#         return render(request,self.template_name,{'form':form})

class VerifyCodeView(View):
    template_name = 'accounts/verify-code.html'
    form_class = UserRegisterCodeForm
    def get(self, request, *args, **kwargs):
        if not request.session.get('allow'):
            messages.error(request,'شما فعالیتی ندارید')
            return redirect('home:home')
        mode = kwargs.get('mode')
        if mode == 'changeemail':
            if not request.user.is_authenticated:
                return HttpResponse("Access Denied: You are not allowed here.")
        messages.success(request,'کد ارسال شد')
        return render(request, self.template_name, {
            'form': self.form_class(),
            'mode': mode,
            'LayOut':True
        })

    def post(self, request, *args, **kwargs):
        mode = kwargs.get('mode')
        form = self.form_class(request.POST)
        if mode == 'register':
            form = self.form_class(request.POST)
            if form.is_valid():
                data = request.session.get('register_data')
                code = request.session.get('register_code')
                if not data or not code:
                    messages.error(request,'session expired')
                    return redirect('accounts:register')
                if int(code) == form.cleaned_data['code']:
                    user = User.objects.create_user(email=data['email'],name=data['name'],
                                                    password=data['password_2'])
                    user.save()
                    login(request,user)
                    messages.success(request,'signed in successfuly')
                    request.session.pop('register_data', None)
                    request.session.pop('register_code', None)
                    request.session['allow'] = False
                    return redirect('home:home')
                else:
                    messages.error(request,'کد تایید اشتباه است')
                    request.session['allow'] = False
                    return redirect('accounts:login')
            if form.errors:
                for field_name, error_list in form.errors.items():
                    for error in error_list:
                        messages.error(request, error)
                for error in form.non_field_errors():
                    messages.error(request, error)
            return render(request,self.template_name,{'form':form})
        elif mode == 'changeemail':
            form = self.form_class(request.POST)
            if form.is_valid():
                session_email = request.session.get('emailchange_data')
                session_code = request.session.get('emailchange_code')

                if not session_email or not session_code:
                    messages.error(request, 'Session expired. Please try again.')
                    return redirect('accounts:changeemail')

                if int(form.cleaned_data['code']) == int(session_code):
                    request.user.email = session_email
                    request.user.save()
                    messages.success(request, 'ایمیل با موفقیت تغییر کرد')

                    # Clean session
                    request.session.pop('emailchange_data', None)
                    request.session.pop('emailchange_code', None)
                    if request.user.is_teacher:
                        return redirect('accounts:teacherprofile', pk=request.user.pk)
                    else:
                        request.session['allow'] = False
                        return redirect('accounts:profile', pk=request.user.pk)
                else:
                    messages.error(request, 'کد اشتباه است')

            if form.errors:
                for field_name, error_list in form.errors.items():
                    for error in error_list:
                        messages.error(request, error)

                for error in form.non_field_errors():
                    messages.error(request, error)

            return render(request, self.template_name, {
                'form': form,
                'LayOut': True
            })



class UserLoginView(View):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    def get(self,request,*args,**kwargs):
        return render(request,self.template_name,{'form':self.form_class(),'LayOut':True,'MU':settings.MEDIA_URL})
    def post(self,request,*args,**kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request,email=data['email'],password=data['password'])
            if user is not None:
                login(request,user)
                messages.success(request,'خوش آمدید')
                return redirect('home:home')
            else:
                messages.error(request,'ایمیل یا رمز اشتباه بود')
                return redirect('accounts:login')
        if form.errors:
            for field_name, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, error)

            for error in form.non_field_errors():
                messages.error(request, error)
        return render(request,self.template_name,{'form':form,'LayOut':True,'MU':settings.MEDIA_URL})

class UserProfileView(LoginRequiredMixin,View):
    template_name = 'accounts/profile.html'
    def get(self,request,*args,**kwargs):
        if self.request.user.is_teacher == True:
            return HttpResponse("Access Denied: You are not allowed here.")
        prof =  get_object_or_404(Profile,user=request.user)
        co = AfterPay.objects.filter(user=request.user)
        if prof.user != request.user:
            return HttpResponse("Access Denied: You are not allowed here.")
        wo = WishList.objects.filter(profile=request.user.profile).prefetch_related('course')

        course_progress = {}
        ended = 0
        for payment in co:
            course = payment.course

            # همه ویدیوهای دوره از طریق title__course
            total_videos = CourseVideo.objects.filter(title__course=course).count()

            # ویدیوهایی که کاربر دیده از همین دوره
            seen_videos = WatchedVideo.objects.filter(user=request.user, course=course, seen='1').count()

            # محاسبه درصد
            percentage = int((seen_videos / total_videos) * 100) if total_videos > 0 else 0
            if percentage==100:
                prof.ended_courses += 1
                prof.documents += 1
            course_progress[course.id] = percentage


        return render(request,self.template_name,{'course_progress':course_progress,'wo':wo,'co':co,'profile':prof,'MU':settings.MEDIA_URL})

class UserChangeProfileView(LoginRequiredMixin,UpdateView):
    template_name = 'accounts/profile.html'
    model = Profile
    fields = ['name','icon']
    def get_object(self, queryset = None):
        if self.request.user.is_teacher:
            return HttpResponse('شما معلم هستید و اجازه دسترسی به این صفحه را ندارید')
        if self.request.user.profile.pk != self.kwargs['pk']:
            return HttpResponse('این صفحه مطعلق به پروفایل شما نیست')
        return Profile.objects.get(user=self.request.user)
    def get_success_url(self):
        if self.request.user.is_teacher:
            return reverse('accounts:teacherprofile', kwargs={'pk': self.request.user.pk})
        else:
            return reverse('accounts:profile',kwargs={'pk':self.request.user.pk})

class TeacherProfileView(TemplateView):
    template_name = 'accounts/teach-profile.html'

    def get_context_data(self, **kwargs):
        if not self.request.user.is_teacher:
            return HttpResponse('شما معلم نیستید')
        context = super().get_context_data(**kwargs)

        teacher = get_object_or_404(TeacherUser, pk=kwargs['pk'])

        # گرفتن تمام ویدیوهای مربوط به دوره‌های این معلم
        videos = CourseVideo.objects.filter(title__course__teacher=teacher)

        # گرفتن همه کامنت‌ها روی اون ویدیوها
        comments = Comments.objects.filter(vid__in=videos).select_related(
            'vid', 'vid__title', 'vid__title__course', 'user'
        )

        # --- فیلتر طبق GET ---
        filter_type = self.request.GET.get('filter', 'all')
        if filter_type == 'answered':
            comments = comments.filter(responded=True)
        elif filter_type == 'unanswered':
            comments = comments.filter(responded=False)

        # لیست ساخت‌یافته برای ارسال به قالب
        structured_comments = []
        for comment in comments:
            try:
                response_obj = comment.respond  # related_name='respond'
                response_text = response_obj.comment
            except RespondedComments.DoesNotExist:
                response_text = None

            structured_comments.append({
                'id': comment.id,
                'course_name': comment.vid.title.course.name,
                'video_name': comment.vid.name or f"جلسه {comment.vid.id}",
                'comment_text': comment.comment,
                'answered': comment.responded,
                'user': comment.user,
                'res':response_text
            })

        context['teach'] = teacher
        context['comments'] = structured_comments
        context['request'] = self.request
        return context

class TeacherQuestionsView(ListView):
    template_name = 'accounts/teacher-questions.html'  # قالب سوالات
    context_object_name = 'comments'

    def get_teacher(self):
        return get_object_or_404(TeacherUser, pk=self.kwargs['pk'])

    def get_queryset(self):
        teacher = self.get_teacher()
        videos = CourseVideo.objects.filter(title__course__teacher=teacher)

        comments = Comments.objects.filter(vid__in=videos).select_related(
            'vid', 'vid__title', 'vid__title__course', 'user'
        )

        filter_type = self.request.GET.get('filter', 'all')
        if filter_type == 'answered':
            comments = comments.filter(responded=True)
        elif filter_type == 'unanswered':
            comments = comments.filter(responded=False)

        return comments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.get_teacher()
        context['teach'] = teacher

        structured_comments = []
        for comment in context['comments']:

            try:
                response_obj = comment.respond  # related_name='respond'
                response_text = response_obj.comment
            except RespondedComments.DoesNotExist:
                response_text = None

            structured_comments.append({
                'id': comment.id,
                'course_name': comment.vid.title.course.name,
                'video_name': comment.vid.name or f"جلسه {comment.vid.id}",
                'comment_text': comment.comment,
                'answered': comment.responded,
                'user': comment.user,
                'res':response_text
            })
        context['comments'] = structured_comments
        return context


class UserChangePasswordView(LoginRequiredMixin,auth_view.PasswordChangeView):
    def get_success_url(self):
        if self.request.user.is_teacher:
            return reverse('accounts:teacherprofile', kwargs={'pk': self.request.user.pk})
        else:
            return reverse('accounts:profile', kwargs={'pk': self.request.user.pk})
    def get_success_url(self):
        if self.request.user.is_teacher:
            return reverse('accounts:teacherprofile', kwargs={'pk': self.request.user.pk})
        else:
            return reverse('accounts:profile',kwargs={'pk':self.request.user.pk})


class TeacherChangeProfileView(LoginRequiredMixin,UpdateView):
    template_name = 'accounts/teach-profile.html'
    model = TeacherUser
    context_object_name = 'teacher'
    fields = ['name','email','number','bio','icon']
    def get_object(self, queryset = None):
        if not self.request.user.is_teacher:
            return HttpResponse('شما معلم نیستید')
        obj = get_object_or_404(TeacherUser, user=self.request.user)
        return get_object_or_404(TeacherUser,user=self.request.user)
    def get_success_url(self):
        if self.request.user.is_teacher:
            return f"{reverse('accounts:teacherprofile', kwargs={'pk': self.request.user.teacher.pk})}?tab=settings"
        else:
            return reverse('accounts:profile',kwargs={'pk':self.request.user.pk})

    def form_valid(self, form):
        number = form.cleaned_data.get('number')

        if not number or number[0] != '0' or number[1] != '9' or len(number) != 11:
            messages.error(self.request, 'شماره خود را صحیح وارد کنید')
            return redirect(f"{reverse('accounts:teacherprofile', kwargs={'pk': self.request.user.teacher.pk})}?tab=settings")
        # Set success URL before saving
        self.success_url = self.get_success_url()
        return super().form_valid(form)

class UserLogoutView(LoginRequiredMixin,auth_view.LogoutView):
    next_page = settings.LOGOUT_REDIRECT_URL

class TeacherCourseUploadView(LoginRequiredMixin, View):
    template_name = 'accounts/teach-profile.html'
    form_class = CourseUploadForm

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            Course.objects.create(
                teacher=request.user.teacher,
                name=data['name'],
                info=data['info'],
                thumbnail=data['thumbnail']  # Ensure your form field name matches this!
            )
            messages.success(request, 'دوره با موفقیت ثبت شد')
            return redirect(reverse('accounts:teacherprofile', kwargs={'pk':request.user.teacher.pk}))
        for errors in form.errors.items():
            if form.errors:
                for field_name, error_list in form.errors.items():
                    for error in error_list:
                        messages.error(request, error)

                for error in form.non_field_errors():
                    messages.error(request, error)
        return render(request, self.template_name, {'form': form})

class UserChangeEmailView(LoginRequiredMixin,View):
    template_name = 'accounts/change-email.html'
    form_class = UserEditEmailForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'form': self.form_class(),

        })

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if User.objects.filter(email=data['email']).exists():
                messages.error(request,'ایمیل از قبل وجود دارد')
                return redirect('accounts:changeemail')
            random_code = randint(100000, 999999)
            email = form.cleaned_data['email']
            request.session['emailchange_data'] = email
            request.session['emailchange_code'] = random_code

            subject = 'Activation Code'
            from_email = 'طراحان OFFSITE <rz1125.1386@gmail.com>'
            to_email = [data['email']]

            # Plain text version (fallback for email clients that don't support HTML)
            text_content = (
                f"{request.user.name}،کاربر گرامی\n"
                f"{random_code}:کد شما\n"
            )

            # HTML version with simple styling
            html_content = f"""
            <html lang="fa" dir="rtl">
            <head>
                <style>
                body {{
                    font-family: 'Tahoma', sans-serif;
                    background-color: #f9f9f9;
                    color: #333;
                    padding: 20px;
                }}
                .container {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    max-width: 600px;
                    margin: auto;
                }}
                h1 {{
                    color: #4CAF50;
                }}
                .code {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #e91e63;
                    margin-top: 20px;
                }}
                p {{
                    line-height: 1.6;
                    font-size: 16px;
                }}
                </style>
            </head>
            <body>
                <div class="container">
                <h1>کاربر گرامی، {request.user.name}</h1>
                <p>کد شما:</p>
                <p class="code">{random_code}</p>
                </div>
            </body>
            </html>
            """

            email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            request.session['allow'] = True
            return redirect('accounts:changeemailcode')
        if form.errors:
            for field_name, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, error)

            for error in form.non_field_errors():
                messages.error(request, error)
        return render(request, self.template_name, {
            'form': form,
            'LayOut': True
        })


class UserCartView(LoginRequiredMixin,View):
    template_name = 'accounts/cart.html'
    def get(self, request, *args, **kwargs):
        cart_id = kwargs.get('pk')

        # If the user is a teacher, deny access
        if getattr(request.user, 'is_teacher', False):
            return HttpResponse('Access Denied')

        # Get user's cart safely
        try:
            cart = request.user.cart
        except Cart.DoesNotExist:
            return HttpResponse('No cart found for this user.')

        # If the URL cart ID doesn't match the user's cart, deny access
        if str(cart.pk) != str(cart_id):
            return HttpResponse('Cart ID mismatch.')

        if not cart.cartitem.exists():
            return render(request, self.template_name, {'LayOutF':True,'MU':settings.MEDIA_URL})

        return render(request, self.template_name, {'ca': cart,'MU':settings.MEDIA_URL})

