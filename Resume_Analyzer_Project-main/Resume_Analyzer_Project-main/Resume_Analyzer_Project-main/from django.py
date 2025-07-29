import fitz  # PyMuPDF
import re


def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def calculate_ats_score(text, keywords):
    score = 0
    matched = []
    for keyword in keywords:
        if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
            score += 10
            matched.append(keyword)
    return min(score, 100), matched

def get_domain_from_keywords(matched_keywords):
    if any(word in matched_keywords for word in ['python', 'django', 'flask']):
        return "Software Developer"
    if any(word in matched_keywords for word in ['ml', 'ai', 'data']):
        return "Data Scientist"
    if any(word in matched_keywords for word in ['marketing', 'seo']):
        return "Digital Marketing"
    return "General"
def signup_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # The form's save method creates the User and Profile
            user = form.save() 

            # This logs the new user in automatically
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created successfully.')
            
            # This redirects the now-logged-in user to the dashboard
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'signup.html', {'form': form})
def signup_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # The form's save method creates the User and Profile
            user = form.save() 

            # This logs the new user in automatically
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created successfully.')
            
            # This redirects the now-logged-in user to the dashboard
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'signup.html', {'form': form})
