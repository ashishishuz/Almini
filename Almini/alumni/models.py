from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

class AlumniProfile(models.Model):
    DESIGNATION_CHOICES = [
        ('student', 'Student'),
        ('working', 'Working Professional'),
        ('teacher', 'Teacher'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='alumni_photos/', null=True, blank=True)
    graduation_year = models.IntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(datetime.now().year)
        ],
        null=False,
        blank=False  # This makes graduation_year mandatory
    )
    department = models.CharField(
        max_length=100,
        null=False,
        blank=False 
     ) # This makes department mandatory)
    # Remove duplicate fields and make fields optional
    current_job = models.CharField(max_length=200, null=True, blank=True)
    company = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    is_mentor = models.BooleanField(default=False)
    designation = models.CharField(
        max_length=20,
        choices=DESIGNATION_CHOICES,
        default='student',
        null=False,
        blank=False  # This makes designation mandatory
    )

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.graduation_year}"

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship')
    ]
    
    STREAM_CHOICES = [
        ('Computer Science', 'Computer Science'),
        ('Information Technology', 'Information Technology'),
        ('Mechanical', 'Mechanical'),
        ('Civil', 'Civil'),
        ('Electronics', 'Electronics'),
        ('Engineering any Stream,','Engineering any stream'),
        ('Management','Management'),
        ('Bachelors degree','Bachelors degree'),
        ('Masters','Masters'),
        ('Other', 'Other')
    ]

    title = models.CharField(max_length=200, null=True, blank=True)
    company_name = models.CharField(max_length=200, null=True, blank=True)
    hiring_workflow = models.TextField(help_text="Describe the hiring process steps")
    apply_link = models.URLField(max_length=500, null=True, blank=True)
    total_openings = models.PositiveIntegerField(default=1,blank=True,null=True)  # mandatory
    location = models.CharField(max_length=200)  # mandatory
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='Internship')  # mandatory
    stream = models.CharField(max_length=50, choices=STREAM_CHOICES, default='Bachelors degree')  # mandatory
    batch_required = models.CharField(max_length=20)  # mandatory
    skills_required = models.TextField()  # mandatory
    responsibilities = models.TextField(null=True, blank=True)
    salary = models.CharField(max_length=50, help_text="Enter salary (e.g., '50000' or '5 LPA' or 'Not Disclosed')")   # mandatory
    experience_required = models.CharField(max_length=50, blank=True, null=True)
    application_deadline = models.DateField()  # mandatory
    posted_by = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    posted_date = models.DateTimeField(auto_now_add=True)
    Recruiter_details = models.TextField(null=True, blank=True, help_text="Enter recruiter contact details including phone numbers and additional information")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"

    class Meta:
        ordering = ['-posted_date']

class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    description = models.TextField()
    organizer = models.CharField(max_length=200)
    speakers = models.CharField(max_length=200, blank=True, null=True)
    capacity = models.PositiveIntegerField(default=1, help_text="Maximum number of attendees allowed", null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class EventAttendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    ATTENDANCE_CHOICES = [
        ('YES', 'Attending'),
        ('NO', 'Not Attending'),
        ('MAYBE', 'Maybe')
    ]
    status = models.CharField(max_length=5, choices=ATTENDANCE_CHOICES)

    class Meta:
        unique_together = ['event', 'alumni']

class SuccessStory(models.Model):
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='liked_stories', blank=True)
    image = models.ImageField(upload_to='success_stories/', null=True, blank=True)
    
class StoryComment(models.Model):
    story = models.ForeignKey(SuccessStory, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class MentorshipRequest(models.Model):
    mentor = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name='mentorship_requests_as_mentor')
    mentee = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name='mentorship_requests_as_mentee')
    message = models.TextField()
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected')
    ]
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mentorship: {self.mentee} -> {self.mentor}"

class Alumni(models.Model):
    mobile_number = models.CharField(max_length=10, help_text="Enter your mobile number")

class Profile(models.Model):
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)


class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    applied_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['job', 'applicant']  # Prevent multiple applications

    def __str__(self):
        return f"{self.applicant.user.get_full_name()} - {self.job.title}"
