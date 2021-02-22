from django.contrib import admin
from .models import Profile, Course, DeliverableFileAttachment, DeliverableLinkAttachment, Deliverable, \
    DeliverableSubmission

# Register your models here.
admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(DeliverableFileAttachment)
admin.site.register(DeliverableLinkAttachment)
admin.site.register(Deliverable)
admin.site.register(DeliverableSubmission)
