from django.contrib import admin
from my_site.models import Contact
from my_site.models import Post_job
from my_site.models import Apply_job
# Register your models here.

admin.site.register(Contact)
admin.site.register(Post_job)
admin.site.register(Apply_job)