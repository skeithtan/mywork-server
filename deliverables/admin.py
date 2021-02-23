from django.contrib import admin
from .models import Profile, Course, FileAttachment, LinkAttachment, Deliverable, \
    DeliverableSubmission

# Register your models here.
admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(FileAttachment)
admin.site.register(LinkAttachment)
admin.site.register(Deliverable)
admin.site.register(DeliverableSubmission)
