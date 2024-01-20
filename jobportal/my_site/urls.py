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
    path('notFound/', notFound, name="404")
]