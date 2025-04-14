from django import forms
from django.core.validators import RegexValidator  # Fixed import
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import AlumniProfile, Job, Event, SuccessStory, MentorshipRequest
from datetime import datetime
# Remove the Profile import since we're using AlumniProfile
# from .models import Profile  # Add this import at the top

class AlumniRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address'})
    )
    graduation_year = forms.IntegerField(
        min_value=1900,
        max_value=datetime.now().year+100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your passing year'}),
        required=True
    )
    department = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your department'})
    )
    mobile_number = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your 10-digit mobile number'}),
        help_text='Enter a valid 10-digit mobile number',
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits."
            )
        ]
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True,  # Making it mandatory
        widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,  # Making it mandatory
        widget=forms.TextInput(attrs={'placeholder': 'Enter your last name(optional)'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
        label='Password'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}),
        label='Confirm Password',
        help_text='Enter the same password as above'
    )
    designation = forms.ChoiceField(choices=[
        ('', 'Select your designation'),
        ('student', 'Student'),
        ('working', 'Working Professional'),
        ('teacher', 'Teacher')
    ])
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'designation','email','department','graduation_year','mobile_number', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter your last name'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            AlumniProfile.objects.create(
                user=user,
                graduation_year=self.cleaned_data['graduation_year'],
                department=self.cleaned_data['department']
            )
        return user

class AlumniProfileForm(forms.ModelForm):
    class Meta:
        model = AlumniProfile
        fields = ['photo', 'current_job', 'company', 'location', 'is_mentor']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional
        for field in self.fields:
            self.fields[field].required = False

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = AlumniProfile
        fields = ['photo', 'current_job', 'company', 'location', 'designation', 'is_mentor']

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company_name', 'location', 'job_type', 'stream', 'batch_required', 
                 'skills_required', 'responsibilities', 'salary', 'experience_required', 
                 'hiring_workflow', 'apply_link', 'total_openings', 'application_deadline','Recruiter_details']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Senior Software Engineer'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Tech Solutions Inc'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Mumbai, India'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('Full-time', 'Full-time'),
                ('Part-time', 'Part-time'),
                ('Contract', 'Contract'),
                ('Internship', 'Internship')
            ]),
             'Recruiter_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter recruiter contact details (phone numbers and additional information)'
            }),
            'stream': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('Computer Science', 'Computer Science'),
                ('Information Technology', 'Information Technology'),
                ('Mechanical', 'Mechanical'),
                ('Civil', 'Civil'),
                ('Electronics', 'Electronics'),
                ('Other', 'Other')
            ]),
            'batch_required': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2020-2024'}),
            'skills_required': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'e.g., Python, JavaScript, React'}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List key job responsibilities'}),
            'salary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter salary (e.g. 50000, 5 LPA, Not Disclosed)',
                'step': '0.01',  # Allow decimal values
                'min': '0'  # Prevent negative values
            }),
            'experience_required': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2-3 years'}),
            'hiring_workflow': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describe the hiring process steps (e.g., 1. Resume Screening, 2. Technical Interview...)'
            }),
            'apply_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter application URL'
            }),
            'total_openings': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter number of openings',
                'min': '1'
            }),
            'application_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_salary(self):
        salary = self.cleaned_data.get('salary')
        if salary and salary < 0:
            raise forms.ValidationError("Salary cannot be negative")
        return salary

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'date', 'location', 'description', 'organizer', 'speakers','capacity']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event title'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event location'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter event description'}),
            'organizer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter organizer name'}),
            'speakers': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter speaker names'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter maximum attendees', 'min': '1'})
        }

class SuccessStoryForm(forms.ModelForm):
    class Meta:
        model = SuccessStory
        fields = ['title', 'content']

class MentorshipRequestForm(forms.ModelForm):
    class Meta:
        model = MentorshipRequest
        fields = ['message']