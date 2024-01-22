from django.shortcuts import render,HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.core.files.storage import FileSystemStorage
from my_site import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, request
from django.urls import reverse
from django.db.models import Count
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from my_site.models import Contact
from my_site.models import Post_job
from my_site.models import Apply_job
import my_site.screen as screen
from django.conf import settings
import os
import PyPDF2
from my_site.models import Apply_job
from my_site.screen import normalize
from my_site.screen import res, read_result_in_json, write_result_in_json
from my_site.text_process import normalize
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

def about(request):
    return render(request, "about.html")


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
        # Extracting data from the POST request
        name = request.POST['name']
        email = request.POST['email']
        # print(name, email)
        gender = request.POST['gender']
        experience = request.POST['experience']
        coverletter = request.POST['coverletter']
        
        # Handling file upload (resume)
        resume = request.FILES['resume']
        print(resume)

        # Deleting existing application for the same user, company, and job title
        Apply_job.objects.filter(name=name, email__exact=email, company_name=job.company_name, title=job.title).delete()

        # Creating a new application instance
        ins = Apply_job(
            name=name,
            email=email,
            resume=resume,
            experience=experience,
            coverletter=coverletter,
            company_name=job.company_name,
            gender=gender,
            title=job.title
        )

        # Saving the new application instance to the database
        ins.save()

        # Displaying a success message and redirecting to the job listings
        messages.info(request, 'Successfully applied for the post!')
        print("The Data is saved into the database!")
        return redirect('job-listings')

    # Rendering the apply job form with details of the selected job
    return render(request, 'my_site/applyjob.html', {'company_name': job.company_name, 'title': job.title})


def ranking(request, id):
    job_data = Post_job.objects.get(id=id)
    print(job_data.id, job_data.title, job_data.company_name)
    jobfilename = job_data.company_name + '_' + job_data.title + '.txt'
    job_desc = job_data.details + '\n' + job_data.responsibilities + '\n' + job_data.experience + '\n';
    resumes_data = Apply_job.objects.filter(company_name=job_data.company_name, title=job_data.title,
                                            resume__isnull=False)
    result_arr = screen.res(resumes_data, job_data)
    print(result_arr)
    return render(request, 'my_site/ranking.html',
                  {'items': result_arr, 'company_name': job_data.company_name, 'title': job_data.title})

# def ranking(request, id):
#     job_data = Post_job.objects.get(id=id)
#     print(job_data.id, job_data.title, job_data.company_name)
#     jobfilename = job_data.company_name + '_' + job_data.title + '.txt'

#     # Store multiple strings in a list
#     job_desc = [job_data.details, job_data.responsibilities, job_data.experience]

#     resumes_data = Apply_job.objects.filter(company_name=job_data.company_name, title=job_data.title,
#                                             resume__isnull=False)

#     # Extract cover letters from resumes_data
#     coverletters = [apply_job.coverletter for apply_job in resumes_data]

#     # Combine job_desc and coverletters into a list of strings
#     all_documents = job_desc + coverletters

#     # Create a TfidfVectorizer and transform the documents
#     vectorizer = TfidfVectorizer(stop_words='english')
#     tfidf_matrix = vectorizer.fit_transform(all_documents)

#     # Calculate cosine similarity between job_desc and coverletters
#     cosine_similarities = linear_kernel(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

#     # Sort the documents by similarity
#     document_scores = list(zip(range(1, len(cosine_similarities) + 1), cosine_similarities))
#     document_scores.sort(key=lambda x: x[1], reverse=True)

#     # Get the sorted list of items
#     result_arr = [item[0] for item in document_scores]

#     return render(request, 'my_site/ranking.html',
#                   {'items': result_arr, 'company_name': job_data.company_name, 'title': job_data.title})

# def extract_text_from_pdf(pdf_path):
#     with open(pdf_path, 'rb') as pdf_file:
#         pdf_reader = PyPDF2.PdfReader(pdf_file)
#         text = ''
#         for page_number in range(len(pdf_reader.pages)):
#             page = pdf_reader.pages[page_number]
#             text += page.extract_text()
#         return text

# def ranking(request, id):
#     try:
#         job_data = Post_job.objects.get(id=id)
#         jobfilename = job_data.company_name + '_' + job_data.title + '.txt'
#         job_desc = job_data.details + '\n' + job_data.responsibilities + '\n' + job_data.experience + '\n'

#         # Normalize job description
#         job_desc_normalized = ' '.join(normalize(job_desc.split()))

#         # Create a dictionary to store results
#         result_dict = {}

#         # Iterate over resumes and calculate scores
#         for apply_job in Apply_job.objects.filter(company_name=job_data.company_name, title=job_data.title,
#                                                   resume__isnull=False):
#             resume_path = str(apply_job.resume.path)
#             try:
#                 resume_text = extract_text_from_pdf(resume_path)
#                 resume_text_normalized = ' '.join(normalize(resume_text.split()))

#                 # Compare job description and resume using TF-IDF or any other similarity measure
#                 # You might want to customize this part based on your specific scoring logic
#                 # ...

#                 # For demonstration purposes, calculate a simple score
#                 score = len(set(job_desc_normalized.split()) & set(resume_text_normalized.split()))

#                 result_dict[apply_job.name] = {'name': apply_job.name, 'score': score}

#             except Exception as e:
#                 print(f"Error extracting text from resume {apply_job.name}: {e}")

#         # Rank candidates and update result_dict
#         # ranked_result_dict = screen.res(resumes_data=list(result_dict.values()), job_data=job_data)
#         ranked_result_dict = screen.res(resumes_data=result_dict, job_data=job_data)

#         # Save the result_dict to a JSON file
#         write_result_in_json(ranked_result_dict, jobfilename)

#         return render(request, 'my_site/ranking.html',
#                       {'items': ranked_result_dict, 'company_name': job_data.company_name, 'title': job_data.title})
#     except Exception as e:
#         print(f"Error in ranking function: {e}")
#         return HttpResponse("Error in ranking function")
    
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

def category(request):
    return render(request, 'category.html')

def testimonial(request):
    return render(request, 'testimonial.html')

def notFound(request):
    return render(request, '404.html')