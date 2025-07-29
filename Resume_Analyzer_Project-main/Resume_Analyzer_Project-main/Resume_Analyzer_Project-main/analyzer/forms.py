from django import forms
from django.contrib.auth.models import User
from .models import Profile, Resume

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create password'}), 
        label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}), 
        label="Confirm Password"
    )
    
    # Add profile fields directly to the registration form
    
    phone = forms.CharField(max_length=20, required=False, label="Phone", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91'}))
    location = forms.CharField(max_length=100, required=False, label="Location", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'San Francisco, CA'}))
    title = forms.CharField(max_length=100, required=False, label="Professional Title", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Frontend Developer'}))
    linkedin = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'LinkedIn Profile URL'})
    )
    github = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GitHub Profile URL'})
    )
    education = forms.ChoiceField(
        choices=[
            ("", "Select education"),
            ("bachelors", "Bachelor's Degree"),
            ("masters", "Master's Degree"),
            ("phd", "PhD"),
            ("other", "Other"),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., John'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'abc@example.com'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

        # Add a CSS class to fields with errors for styling
        for field_name in self.errors:
            field = self.fields.get(field_name)
            if field:
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{existing_classes} is-invalid'.strip()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        if password and password2 and password != password2:
            self.add_error('password2', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        # First, save the User object
        user = super().save(commit=False)
        user.username = self.cleaned_data['email'] # Use email for username
        user.set_password(self.cleaned_data["password"])  # set and hash password
        if commit:
            user.save()

        # Now, robustly create or update the profile
        # This prevents the IntegrityError by fetching the profile if it already exists (e.g., from a signal)
        profile, created = Profile.objects.get_or_create(user=user)
        profile.phone = self.cleaned_data.get('phone', '')
        profile.location = self.cleaned_data.get('location', '')
        profile.title = self.cleaned_data.get('title', '')
        profile.education = self.cleaned_data.get('education', '')
        profile.save()

        return user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("An account with this email already exists. Please use a different email or log in.")
        return email

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        # Re-ordered for better flow in the form
        fields = ['title', 'phone', 'location', 'education', 'github', 'linkedin']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Senior Software Engineer'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 1234567890'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., San Francisco, CA'}),
            'github': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/username'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/username'}),
        }

    # Use a ChoiceField for a better user experience, consistent with the signup form
    education = forms.ChoiceField(
        choices=[
            ("", "Select education"),
            ("bachelors", "Bachelor's Degree"),
            ("masters", "Master's Degree"),
            ("phd", "PhD"),
            ("other", "Other"),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']
