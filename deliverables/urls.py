from django.urls import path, re_path, include
from . import views
from django.conf.urls import url 
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# schema_view = get_swagger_view(title='MyWork API')


schema_view = get_schema_view(
   openapi.Info(
      title="MyWork API",
      default_version='v1',
      description="This is the API documentation of MyWork",
      terms_of_service="https://www.google.com/policies/terms/",
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('auth/sign-in/', views.sign_in_view),
    path('auth/sign-up/',views.create_profile_view),
    path('profile/', views.get_profile_view),
    path('deliverables/', views.create_deliverable_view),
    path('deliverables/submissions/',views.get_student_deliverable_submissions_view),
    path('deliverables/submissions/<id>/members',views.members_view),
    path('courses/', views.courses_view),
    path('courses/<id>', views.courses_details_view),
    path('courses/<id>/deliverables/',views.course_deliverables_view),
    path('deliverables/<deliverable_id>/submissions/',views.get_professor_deliverables_submissions_view),
    path('deliverables/submissions/<id>/link-attachments', views.link_attachment_view),
    path('deliverables/submissions/<id>/link-attachments/<link_id>', views.link_delete_view),
    path('deliverables/submissions/<id>/', views.grade_view),
    re_path(r'^doc(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),  #<-- Here
    path('doc/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),  #<-- Here
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),  #<-- Here
]
