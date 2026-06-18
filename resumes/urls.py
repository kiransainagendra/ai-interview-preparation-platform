from django.urls import path
from .views import upload_resume, resume_result

urlpatterns = [
    path('upload/', upload_resume, name='upload_resume'),
    path('result/<int:resume_id>/', resume_result, name='resume_result'),
]