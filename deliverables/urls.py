from django.urls import path
from . import views

urlpatterns = [
    path('auth/sign-in/', views.sign_in_view),
    path('auth/sign-up/', views.create_profile_view),
    path('profile/', views.get_profile_view),
    path('deliverables/submissions/', views.get_student_deliverable_submissions_view),
    path('courses/', views.get_courses_view),
    path('create-course/', views.create_course)

]
