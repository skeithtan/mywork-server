from django.urls import path
from . import views

urlpatterns = [
    path('auth/sign-in/', views.sign_in_view),
    path('auth/sign-up/', views.create_profile_view),
    path('profile/', views.get_profile_view),
    path('deliverables/', views.create_deliverable_view),
    path('deliverables/submissions/', views.get_student_deliverable_submissions_view),
    path('deliverables/submissions/<id>/members', views.members_view),
    path('courses/', views.courses_view),
    path('courses/<id>', views.courses_details_view),
    path('courses/<id>/deliverables/', views.course_deliverables_view)
]
