from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django import forms
from django.views.decorators.csrf import csrf_exempt
from .utils.gemini import generate_interview_questions
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from .forms import RegisterForm, ProfileForm, ResumeForm
from .models import Resume, Profile, Activity, JobApplication
import json
from analyzer.utils.gemini import generate_interview_questions
from django.contrib.auth.models import User  # ✅ make sure you import this
from .ats_utils import extract_text_from_pdf
from analyzer.utils.resume_analysis import analyze_resume_score
import os


def landing_page(request):
    return render(request, 'landingpage.html')

# 🔑 Login
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        linkedin = request.POST.get('linkedin', '').strip()
        github = request.POST.get('github', '').strip()
        
        # Your signup form sets the username to be the email, so we can authenticate directly.
        # This is more robust and avoids the MultipleObjectsReturned error.
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    return render(request, 'login.html')
  

# 🚪 Logout
def logout_view(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save() # The form's save method now handles User and Profile creation

            # Log the user in automatically after registration and redirect to the dashboard
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created successfully.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'signup.html', {'form': form})

# 🏠 Dashboard
@login_required
def dashboard(request):
    resumes = Resume.objects.filter(user=request.user).order_by('-uploaded_at')
    resume_count = resumes.count()

    latest_resume = resumes.first() if resumes.exists() else None
    skill_score = latest_resume.ats_score if latest_resume else None  # Default skill score if no resume exists
    
    # Job Application Tracker Data
    # Fetch all applications for the user in a single query for efficiency
    applications_list = list(JobApplication.objects.filter(user=request.user))
    
    # Calculate counts in Python to avoid multiple database hits
    applied_count = len(applications_list)
    interviews_count = sum(1 for app in applications_list if app.status == 'Interviewing')
    offers_count = sum(1 for app in applications_list if app.status == 'Offer')
    pending_count = sum(1 for app in applications_list if app.status in ['Applied', 'Interviewing'])

    # Domain-wise Progress
    skill_domains = [
        {'name': 'Web Development', 'progress': 0, 'icon': 'fas fa-code'},
        {'name': 'Data Science', 'progress': 0, 'icon': 'fas fa-brain'},
        {'name': 'Android Development', 'progress': 0, 'icon': 'fab fa-android'},
        {'name': 'UI/UX Design', 'progress': 0, 'icon': 'fas fa-drafting-compass'},
        {'name': 'DevOps', 'progress': 0, 'icon': 'fas fa-server'},
        {'name': 'Public Speaking', 'progress': 0, 'icon': 'fas fa-microphone-alt'},
        {'name': 'Digital Marketing', 'progress': 0, 'icon': 'fas fa-bullhorn'},
    ]

    if latest_resume and latest_resume.domain and latest_resume.domain != "General":
        for domain in skill_domains:
            if domain['name'] == latest_resume.domain:
                domain['progress'] = latest_resume.ats_score or 0
                break  # Found the domain, no need to loop further
    # Learning Recommendations Logic
    learning_recommendations = []
    if latest_resume and latest_resume.domain and latest_resume.domain != "General":
        domain = latest_resume.domain
        if domain == "Web Development":
            learning_recommendations = [
                {'icon': 'fas fa-book', 'label': 'Learn', 'text': 'Data Structures'},
                {'icon': 'fas fa-server', 'label': 'Master', 'text': 'System Design'},
                {'icon': 'fas fa-cloud', 'label': 'Explore', 'text': 'Cloud Platforms'},
                {'icon': 'fas fa-shield-alt', 'label': 'Study', 'text': 'API Security'}
            ]
        elif domain == "Data Scientist":
            learning_recommendations = [
                {'icon': 'fas fa-chart-line', 'label': 'Learn', 'text': 'ML Algorithms'},
                {'icon': 'fas fa-database', 'label': 'Master', 'text': 'SQL & Big Data'},
                {'icon': 'fas fa-eye', 'label': 'Explore', 'text': 'Data Visualization'},
                {'icon': 'fas fa-brain', 'label': 'Study', 'text': 'Deep Learning'}
            ]
    else: # Default recommendations if no specific domain
        learning_recommendations = [
            {'icon': 'fas fa-file-alt', 'label': 'Improve', 'text': 'Resume Keywords'},
            {'icon': 'fas fa-user-tie', 'label': 'Practice', 'text': 'Behavioral Qs'},
            {'icon': 'fab fa-linkedin', 'label': 'Network', 'text': 'On LinkedIn'},
            {'icon': 'fas fa-building', 'label': 'Research', 'text': 'Target Companies'}
        ]

    activities = Activity.objects.filter(user=request.user)[:5] # Get the 5 most recent activities
    username = request.user.first_name
    return render(request, 'dashboard.html', {
        'resumes': resumes,
        'resume_count': resume_count,
        'latest_resume': latest_resume,
        'skill_score': skill_score,  # Pass the skill score to the template
        'activities': activities,
        'applied_count': applied_count,
        'interviews_count': interviews_count,
        'offers_count': offers_count,
        'pending_count': pending_count,
        'learning_recommendations': learning_recommendations,
        'skill_domains': skill_domains,
    })



# 📁 Upload Resume
@login_required
def upload_resume(request):
    resumes = Resume.objects.filter(user=request.user).order_by('-uploaded_at')
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            score, domain = analyze_resume_score(resume.file)
            resume.ats_score = score
            resume.domain = domain
           
            resume.save()

            # Log this action as an activity
            Activity.objects.create(
                user=request.user,
                activity_type="Uploaded Resume",
                description=f"{resume.file.name.split('/')[-1]} ({domain})",
                icon_class="fas fa-upload"
            )

            ats_score = resume.ats_score
            messages.success(request, 'Resume uploaded and analyzed successfully!')
            resumes = Resume.objects.filter(user=request.user).order_by('-uploaded_at') # Re-query to get the latest list
            return render(request, 'upload_resume.html', {'form': form, 'ats_score': ats_score, 'resumes': resumes})
    else:
        form = ResumeForm()
        ats_score = None  # Ensure ats_score is defined even when the form is not submitted

    return render(request, 'upload_resume.html', {'form': form, 'ats_score': ats_score, 'resumes': resumes})

@login_required
def delete_resume(request, resume_id):
    # Use get_object_or_404 to safely retrieve the resume or return a 404 error
    resume = get_object_or_404(Resume, id=resume_id)

    # Security check: ensure the user deleting the resume is the one who uploaded it
    if resume.user != request.user:
        messages.error(request, "You are not authorized to delete this resume.")
        return redirect('upload_resume')

    # Get the filename before we delete the resume object, to find the activity
    resume_filename = resume.file.name.split('/')[-1] # e.g., 'my_resume.pdf'
    activity_description = f"{resume_filename} ({resume.domain})"

    resume.file.delete(save=False)  # Delete the actual file from storage
    resume.delete()  # Delete the resume record from the database

    # Also delete the corresponding "Uploaded Resume" activity.
    # We find the most recent activity matching the description to be safe,
    # in case multiple files had the same name.
    activity_to_delete = Activity.objects.filter(
        user=request.user,
        activity_type="Uploaded Resume",
        description=activity_description
    ).order_by('-timestamp').first()
    if activity_to_delete:
        activity_to_delete.delete()

    messages.success(request, "Resume deleted successfully.")
    return redirect('upload_resume')

# 👤 Profile
@login_required
def profile(request):
    profile = request.user.profile  # Profile model
    return render(request, 'profile.html', {'profile': profile})

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        # Pass request.FILES to handle potential file uploads (like a profile picture) in the future
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        # For a GET request, populate the form with the user's current profile data
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

# 💼 Job Matcher
@login_required
def job_matcher(request):
    return render(request, 'jobmatcher.html')

# 🤖 Interview Prep (Placeholder)
@login_required
def interview_prep(request):
   ''' questions = [
        #"Tell me about a challenging project you've worked on.",
       # "What is your experience with Django and Python?",
       # "How do you handle version control using Git?",
       # "Explain the MVC pattern in Django.",
       # "How do you optimize database queries?"
    ]
    selected_domain = None

    if request.method == 'POST':
        domain = request.POST.get('domain')
        if selected_domain:
            questions = generate_interview_questions(domain)

    return render(request, 'interview_prep.html', {
        'questions': questions,
        
    })'''
   return render(request, 'interview_prep.html')

def generate_questions(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            domain = data.get("domain", "")
            count = int(data.get("count", 10))
          #  questions = generate_interview_questions(domain, count)
            # ✅ Dummy questions – replace with Gemini later
            questions = generate_interview_questions(domain, count)
                
        
            return JsonResponse({'questions': questions})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
        


# 📄 Download Interview Questions as PDF (Placeholder)
@login_required
def download_questions_pdf(request):
    return HttpResponse("PDF download feature coming soon.")
