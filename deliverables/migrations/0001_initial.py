# Generated by Django 3.1.7 on 2021-02-23 08:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('semester_name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Deliverable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('is_group_work', models.BooleanField()),
                ('description', models.TextField()),
                ('deadline', models.DateTimeField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('total_score', models.PositiveIntegerField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deliverables.course')),
            ],
        ),
        migrations.CreateModel(
            name='FileAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='deliverable-file-attachments/')),
                ('label', models.CharField(blank=True, max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='LinkAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=1024)),
                ('label', models.CharField(blank=True, max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('user_type', models.CharField(choices=[('ST', 'Student'), ('PR', 'Professor')], max_length=2)),
                ('program', models.CharField(blank=True, max_length=128)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DeliverableSubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_submitted', models.DateTimeField(blank=True, null=True)),
                ('score', models.PositiveIntegerField(blank=True, null=True)),
                ('feedback', models.TextField(blank=True)),
                ('student_has_seen_feedback', models.BooleanField(default=False)),
                ('deliverable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deliverables.deliverable')),
                ('file_attachments', models.ManyToManyField(blank=True, to='deliverables.FileAttachment')),
                ('group_members', models.ManyToManyField(related_name='deliverable_submission_group_members_set', to='deliverables.Profile')),
                ('link_attachments', models.ManyToManyField(blank=True, to='deliverables.LinkAttachment')),
                ('submitter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deliverable_submission_submitter_set', to='deliverables.profile')),
            ],
        ),
        migrations.AddField(
            model_name='deliverable',
            name='file_attachments',
            field=models.ManyToManyField(blank=True, to='deliverables.FileAttachment'),
        ),
        migrations.AddField(
            model_name='deliverable',
            name='link_attachments',
            field=models.ManyToManyField(blank=True, to='deliverables.LinkAttachment'),
        ),
        migrations.AddField(
            model_name='course',
            name='professor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='course_professor_set', to='deliverables.profile'),
        ),
        migrations.AddField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(related_name='course_student_set', to='deliverables.Profile'),
        ),
    ]
