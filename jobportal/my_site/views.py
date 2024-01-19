from django.shortcuts import render

# Create your views here.
# def index(request):
#     return render(request, 'my_site/index.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.core.files.storage import FileSystemStorage
from my_site import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, request
from django.urls import reverse
from django.db.models import Count

from my_site.models import Contact
from my_site.models import Post_job
from my_site.models import Apply_job
import my_site.screen as screen
import re
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView


# write your code
def index(request):
    job_list = Post_job.objects.get_queryset().order_by('id')
    total_jobs = job_list.count()
    total_users = User.objects.all().count()
    total_companies = Post_job.objects.values('company_name').annotate(Count('company_name', distinct=True))
    query_num = 5
    paginator = Paginator(job_list, query_num)
    page = request.GET.get('page')
    try:
        qs = paginator.page(page)
    except PageNotAnInteger:
        qs = paginator.page(1)
    except EmptyPage:
        qs = paginator.page(paginator.num_pages)
    if qs.has_previous():
        page_show_min = (qs.previous_page_number() - 1) * query_num + 1
    elif total_jobs > 0:
        page_show_min = 1
        
    else:
        page_show_min = 0
    if qs.has_next():
        page_show_max = (qs.previous_page_number() + 1) * query_num - 1
    else:
        page_show_max = total_jobs
    context = {
        'query': qs,
        'job_listings': job_list,
        'job_len': total_jobs,
        'curr_page1': page_show_min,
        'curr_page2': page_show_max,
        'companies': total_companies.count(),
        'candidates': total_users
    }
    return render(request, "my_site/index.html", context=context)


def job_listings(request):
    job_list = Post_job.objects.get_queryset().order_by('id')
    total_jobs = job_list.count()
    total_users = User.objects.all().count()
    total_companies = Post_job.objects.values('company_name').annotate(Count('company_name', distinct=True))
    query_num = 7
    paginator = Paginator(job_list, query_num)
    page = request.GET.get('page')
    try:
        qs = paginator.page(page)
    except PageNotAnInteger:
        qs = paginator.page(1)
    except EmptyPage:
        qs = paginator.page(paginator.num_pages)
    if qs.has_previous():
        page_show_min = (qs.previous_page_number() - 1) * query_num + 1
    elif total_jobs > 0:
        page_show_min = 1
    else:
        page_show_min = 0
    if qs.has_next():
        page_show_max = (qs.previous_page_number() + 1) * query_num - 1
    else:
        page_show_max = total_jobs
    context = {
        'query': qs,
        'job_listings': job_list,
        'job_len': total_jobs,
        'curr_page1': page_show_min,
        'curr_page2': page_show_max,
        'companies': total_companies.count,
        'candidates': total_users
    }
    return render(request, "my_site/job-listings.html", context=context)


# def post_job(request):
#     if request.method == "POST":
#         title = request.POST['title']
#         company_name = request.POST['company_name']
#         employment_status = request.POST['employment_status']
#         vacancy = request.POST['vacancy']
#         gender = request.POST['gender']
#         if 'details' in request.POST:
#             details = request.POST['details']
#         else:
#             details = False
#         if 'responsibilities' in request.POST:
#             responsibilities = request.POST['responsibilities']
#         else:
#             responsibilities = False
#         experience = request.POST['experience']
#         other_benefits = request.POST['other_benefits']
#         job_location = request.POST['job_location']
#         salary = request.POST['salary']
#         application_deadline = request.POST['application_deadline']
#         job = Post_job.objects.filter(title=title, company_name=company_name, employment_status=employment_status)
#         print(job)
#         if not job:
#             ins = Post_job(title=title, company_name=company_name, employment_status=employment_status, vacancy=vacancy,
#                           gender=gender, details=details,
#                           responsibilities=responsibilities, experience=experience, other_benefits=other_benefits,
#                           job_location=job_location, salary=salary, application_deadline=application_deadline)
#             ins.save()
#             messages.info(request, 'Job successfully posted!')
#             print("The data has been added into the database!")
#         else:
#             messages.info(request, 'This job is already posted!')
#             print('This job is already posted!')
#         return redirect('job-listings')
#     return render(request, 'my_site/post-job.html', {})

def post_job(request):
    if request.method == "POST":
        title = request.POST['title']
        company_name = request.POST['company_name']
        employment_status = request.POST['employment_status']
        vacancy = request.POST.get('vacancy', '')  # Modify this line
        gender = request.POST['gender']
        details = request.POST.get('details', '')
        responsibilities = request.POST.get('responsibilities', '')
        experience = request.POST['experience']
        other_benefits = request.POST['other_benefits']
        job_location = request.POST['job_location']
        salary = request.POST['salary']
        application_deadline = request.POST['application_deadline']

        job = Post_job.objects.filter(title=title, company_name=company_name, employment_status=employment_status)
        
        if not job:
            ins = Post_job(
                title=title, company_name=company_name, employment_status=employment_status, vacancy=vacancy,
                gender=gender, details=details, responsibilities=responsibilities, experience=experience,
                other_benefits=other_benefits, job_location=job_location, salary=salary,
                application_deadline=application_deadline
            )
            ins.save()
            messages.info(request, 'Job successfully posted!')
            print("The data has been added into the database!")
        else:
            messages.info(request, 'This job is already posted!')
            print('This job is already posted!')
        return redirect('job-listings')
    
    return render(request, 'my_site/post-job.html', {})


def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        if 'phone' in request.POST:
            phone = request.POST['phone']
        else:
            phone = False

        if 'subject' in request.POST:
            subject = request.POST['subject']
        else:
            subject = False

        if 'desc' in request.POST:
            desc = request.POST['desc']
        else:
            desc = False

        ins = Contact(name=name, email=email, phone=phone, subject=subject, desc=desc)
        ins.save()
        print("Data has been saved in the database!")
        return redirect('/')

    else:
        return render(request, "my_site/contact.html")


def applyjob(request, id):
    job = Post_job.objects.get(id=id)
    print(job.id)
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        print(name, email)
        gender = request.POST['gender']
        experience = request.POST['experience']

        coverletter = request.POST['coverletter']
        cv = request.FILES['cv']
        print(cv)
        print(cv)
        Apply_job.objects.filter(name=name, email__exact=email, company_name=job.company_name, title=job.title).delete()
        ins = Apply_job(name=name, email=email, cv=cv, experience=experience, coverletter=coverletter,
                        company_name=job.company_name, gender=gender,
                        title=job.title)
        ins.save()
        messages.info(request, 'Successfully applied for the post!')
        print("The Data is saved into the database!")
        return redirect('job-listings')

    return render(request, 'my_site/applyjob.html', {'company_name': job.company_name, 'title': job.title})


def ranking(request, id):
    job_data = Post_job.objects.get(id=id)
    print(job_data.id, job_data.title, job_data.company_name)
    jobfilename = job_data.company_name + '_' + job_data.title + '.txt'
    job_desc = job_data.details + '\n' + job_data.responsibilities + '\n' + job_data.experience + '\n';
    resumes_data = Apply_job.objects.filter(company_name=job_data.company_name, title=job_data.title,
                                            cv__isnull=False)
    result_arr = screen.res(resumes_data, job_data)
    return render(request, 'my_site/ranking.html',
                  {'items': result_arr, 'company_name': job_data.company_name, 'title': job_data.title})

class SearchView(ListView):
    model = Post_job
    template_name = 'mysite/search.html'
    context_object_name = 'all_job'

    def get_queryset(self):
        return self.model.objects.filter(title__contains=self.request.GET['title'],
                                         job_location__contains=self.request.GET['job_location'],
                                         employment_status__contains=self.request.GET['employment_status'])
    
def job_single(request, id):
    job_query = Post_job.objects.get(id=id)
    context = {
        'q': job_query,
    }
    return render(request, "my_site/job-single.html", context)