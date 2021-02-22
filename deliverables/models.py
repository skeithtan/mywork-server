from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    class UserType(models.TextChoices):
        STUDENT = 'ST', _('Student')
        PROFESSOR = 'PR', _('Professor')

    name = models.CharField(max_length=128)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=2, choices=UserType.choices)
    program = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.user} - {self.program}"


class Course(models.Model):
    name = models.CharField(max_length=128)
    semester_name = models.CharField(max_length=128)
    professor = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='course_professor_set')
    students = models.ManyToManyField(Profile, related_name='course_student_set')


class DeliverableFileAttachment(models.Model):
    file = models.FileField(upload_to='deliverable-file-attachments/')
    label = models.CharField(max_length=128, blank=True)


class DeliverableLinkAttachment(models.Model):
    url = models.CharField(max_length=1024)
    label = models.CharField(max_length=128, blank=True)


class Deliverable(models.Model):
    name = models.CharField(max_length=128)
    course = models.ManyToManyField(Course)
    is_group_work = models.BooleanField()
    description = models.TextField()
    link_attachments = models.ManyToManyField(DeliverableLinkAttachment)
    file_attachments = models.ManyToManyField(DeliverableFileAttachment)
    deadline = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True)
    total_score = models.PositiveIntegerField()


class DeliverableSubmission(models.Model):
    deliverable = models.ManyToManyField(Deliverable)
    submitter = models.ManyToManyField(Profile, related_name='deliverable_submission_submitter_set')
    group_members = models.ManyToManyField(Profile, related_name='deliverable_submission_group_members_set')
    date_submitted = models.DateTimeField(null=True)
    file_attachments = models.ManyToManyField(DeliverableFileAttachment)
    link_attachments = models.ManyToManyField(DeliverableLinkAttachment)
    score = models.PositiveIntegerField()
    feedback = models.TextField(blank=True)
    student_has_seen_feedback = models.BooleanField(default=False)
