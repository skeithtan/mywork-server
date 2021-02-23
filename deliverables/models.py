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
    program = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f"{self.user} - {self.program if self.user_type == Profile.UserType.STUDENT else 'Professor'}"


class Course(models.Model):
    name = models.CharField(max_length=128)
    semester_name = models.CharField(max_length=128)
    professor = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name='course_professor_set')
    students = models.ManyToManyField(Profile, related_name='course_student_set')

    def __str__(self):
        return f"{self.name} - {self.semester_name}"


class FileAttachment(models.Model):
    file = models.FileField(upload_to='deliverable-file-attachments/')
    label = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.label


class LinkAttachment(models.Model):
    url = models.CharField(max_length=1024)
    label = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.label


class Deliverable(models.Model):
    name = models.CharField(max_length=128)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_group_work = models.BooleanField()
    description = models.TextField()
    link_attachments = models.ManyToManyField(LinkAttachment, blank=True)
    file_attachments = models.ManyToManyField(FileAttachment, blank=True)
    deadline = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True)
    total_score = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.course.name}"


class DeliverableSubmission(models.Model):
    deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE)
    submitter = models.ForeignKey(Profile,
                                  related_name='deliverable_submission_submitter_set',
                                  on_delete=models.CASCADE)

    group_members = models.ManyToManyField(Profile, related_name='deliverable_submission_group_members_set')
    date_submitted = models.DateTimeField(blank=True, null=True)
    file_attachments = models.ManyToManyField(FileAttachment, blank=True)
    link_attachments = models.ManyToManyField(LinkAttachment, blank=True)
    score = models.PositiveIntegerField(blank=True, null=True)
    feedback = models.TextField(blank=True)
    student_has_seen_feedback = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.deliverable.name} -- {self.submitter.name}"
