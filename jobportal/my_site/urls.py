from django.contrib import admin
from django.urls import path
from my_site.views import (
    index,
    about,
    job_single,
    job_listings,
    post_job,
    contact,
    applyjob,
    ranking,
    SearchView,
    category,
    testimonial,
    notFound,
    view_resume,
    upload_and_chat
)

urlpatterns = [
    path('', index, name="index"),
    path('about/', about, name="about"),
    path('job-listings/', job_listings, name="job-listings"),
    path('job-single/<int:id>/', job_single, name="job_single"),
    path('post-job/', post_job, name="post-job"),
    path('contact/', contact, name="contact"),
    path('applyjob/<int:id>/', applyjob, name="applyjob"),
    path('ranking/<int:id>/', ranking, name="ranking"),
    path('search/', SearchView.as_view(), name='search'),
    path('category/', category, name="category"),
    path('testimonial/', testimonial, name="testimonial"),
    # path('view-resume/<int:apply_job_id>/', view_resume, name='view_resume'),
    path('view-resume/<str:candidate_name>/', view_resume, name = 'view_resume'),
    path('notFound/', notFound, name="404"),
    # chat with pdf urls
    path('upload-and-chat/', upload_and_chat, name = 'upload_and_chat')
]