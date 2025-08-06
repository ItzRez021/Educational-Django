from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,DetailView
from django.conf import settings
from .models import Blog,ContactUs,NewsMate
from courses.models import Course,Comments
from django.contrib import messages
from .forms import ContactUsForm,ContactUsHomeForm,NewsMateForm,IndexContactUsForm
from accounts.models import TeacherUser

class HomePage(View):
    template_name = 'home/index.html'
    form_class = IndexContactUsForm
    def get(self,request):
        co = Course.objects.all()
        cou = 0
        for i in co:
            cou += i.students.all().count()
        teachers = TeacherUser.objects.all()
        allrate = Comments.objects.all().count()
        if allrate != 0:
            allrate += (allrate)*100/co.count()
        return render(request,self.template_name,{'form':self.form_class(),'MU':settings.MEDIA_URL,'co':co,'cou':cou,
                                                  'teach':teachers,'rate':allrate})
    def post(self,request,*args,**kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if ContactUs.objects.filter(user=request.user).exists():
                messages.error(request,'شما یک تیکت باز دارید')
                return render(request, self.template_name, {'form': form, 'MU': settings.MEDIA_URL})
            else:
                    cont = ContactUs.objects.create(user=request.user,name=data['name'],email=data['email'],req_pm=data['req_pm'])
                    messages.success(request,'تیکت شما ثبت شد')
                    cont.save()
                    return redirect('home:home')
        if form.errors:
            for field_name, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, error)

            for error in form.non_field_errors():
                messages.error(request, error)
        return render(request,self.template_name,{'form':form,'MU':settings.MEDIA_URL})


def course_search(request):
    query = request.GET.get('q', '')
    if query:
        Co = Course.objects.filter(name__icontains=query)
    else:
        Co = Course.objects.all()
    return render(request, 'courses/packages.html', {'Co': Co})



class ContactUsView(LoginRequiredMixin,View):
    template_name = 'home/contact-to-us.html'
    form_class = ContactUsForm
    def get(self,request):
        return render(request,self.template_name,{'form':self.form_class(),'MU':settings.MEDIA_URL})
    def post(self,request,*args,**kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if ContactUs.objects.filter(user=request.user).exists():
                messages.error(request,'شما یک تیکت باز دارید')
                return render(request, self.template_name, {'form': form, 'MU': settings.MEDIA_URL})
            else:
                if data['check']:
                    cont = ContactUs.objects.create(user=request.user,name=data['name'],email=data['email'],number=data['number'],
                                                    req_title=data['req_title'],req_pm=data['req_pm'])
                    messages.success(request,'تیکت شما ثبت شد')
                    cont.save()
                    return redirect('home:contactus')
                else:
                    messages.error(request,'با قوانین موافقت کنید')
                    return redirect('home:contactus')

        if form.errors:
            for field_name, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, error)

            for error in form.non_field_errors():
                messages.error(request, error)
        return render(request,self.template_name,{'form':form,'MU':settings.MEDIA_URL})


class BlogView(ListView):
    template_name = 'home/blog.html'
    context_object_name = 'blog'
    model = Blog
    form_class = NewsMateForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['MU'] = settings.MEDIA_URL
        return context
    def post(self,request,*args,**kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if NewsMate.objects.filter(email=data['email']).exists():
                messages.error(request,'شما قبلا عضو شده اید')
                return redirect('home:blog')
            else:
                new = NewsMate.objects.create(user=request.user,email=data['email'])
                new.save()
                messages.success(request,'شما به خبرنامه عضو شدید')
                return redirect('home:blog')

        if form.errors:
            for field_name, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, error)

            for error in form.non_field_errors():
                messages.error(request, error)
        return render(request,self.template_name,{'form':form})


class BlogPostView(DetailView):
    template_name = 'home/blog-post.html'
    context_object_name = 'blog'
    model = Blog
    def get_object(self,queryset=None):
        return get_object_or_404(Blog,pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['MU'] = settings.MEDIA_URL
        return context

class RulesView(View):
    template_name = 'home/rulls.html'
    def get(self,request):
        return render(request,self.template_name,{'MU':settings.MEDIA_URL})

class PrivacyView(View):
    template_name = 'home/privacy.html'
    def get(self,request):
        return render(request,self.template_name,{'MU':settings.MEDIA_URL})


class NewsMatecontactusView(LoginRequiredMixin,View):
    template_name = "home/contact-to-us.html"
    form_class = NewsMateForm
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if NewsMate.objects.filter(email=data['email']).exists():
                messages.error(request,'شما قبلا عضو شده اید')
                return redirect('courses:allcourses')
            else:
                new = NewsMate.objects.create(user=request.user,email=data['email'])
                new.save()
                messages.success(request,'شما به خبرنامه عضو شدید')
                return redirect('home:contactus')
        if form.errors:
            for field_name, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, error)

            for error in form.non_field_errors():
                messages.error(request, error)
        return render(request,self.template_name,{'form':form})