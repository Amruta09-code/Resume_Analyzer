from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import upload_resume

urlpatterns = [
    # path('', RedirectView.as_view(url='login/', permanent=False)), 
    
    path('', views.landing_page, name='landing_page'), # 👈 ADD THIS LINE
    

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('resumes/<int:resume_id>/delete/', views.delete_resume, name='delete_resume'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('interview-prep/', views.interview_prep, name='interview_prep'),
    path('generate-questions/', views.generate_questions, name='generate_questions'),
    path('job-matcher/', views.job_matcher, name='job_matcher'),
    path('download-questions-pdf/', views.download_questions_pdf, name='download_questions_pdf'),

    # Password Reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name="password_reset_form.html"), 
         name="password_reset"),

    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), 
         name="password_reset_done"),

    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), 
         name="password_reset_confirm"),

    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), 
         name="password_reset_complete"),
]
