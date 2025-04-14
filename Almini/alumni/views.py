from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta,date
from django.db import models
from django.db.models import Q
from .models import (
    AlumniProfile, Job, Event, EventAttendance, 
    SuccessStory, MentorshipRequest, StoryComment
)
from .forms import (
    AlumniRegistrationForm, AlumniProfileForm, JobForm, 
    EventForm, SuccessStoryForm, MentorshipRequestForm
)
from django.utils.timezone import make_aware, is_naive
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from .forms import ProfileUpdateForm 
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
import json
from django.shortcuts import render, get_object_or_404
from .models import Job
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return redirect('alumni:login')

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view


def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    return render(request, 'alumni/job_detail.html', {'job': job})


def home(request):
    current_hour = datetime.now().hour
    greeting = "Good Morning" if current_hour < 12 else "Good Afternoon" if current_hour < 16 else "Good Evening"
    success_stories = SuccessStory.objects.filter(is_approved=True).order_by('-date_posted')[:1]
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:1]
    # Get only the latest event
    latest_event = Event.objects.filter(
        date__gte=timezone.now()
    ).order_by('date').first()
    
    # Get only the latest success story
    latest_success_story = SuccessStory.objects.filter(is_approved=True).order_by('-date_posted').first()
    return render(request, 'alumni/home.html', {
        'success_stories': success_stories,
        'upcoming_events': upcoming_events,
        'user':request.user,
        'greeting': greeting,  
        'latest_event':latest_event,
        'latest_success_story': latest_success_story,
        
    })
     

# Remove @login_required from register view
def register(request):
    if request.method == 'POST':
        form = AlumniRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered. Please use a different email or login.', extra_tags='popup')
                return render(request, 'registration/register.html', {'form': form})
            form.save()
            messages.success(request, 'Registration successful! Please log in.', extra_tags='popup')
            return redirect('login')
    else:
        form = AlumniRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    profile = get_object_or_404(AlumniProfile, user=request.user)
    if request.method == 'POST':
        form = AlumniProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('alumni:profile')
    else:
        form = AlumniProfileForm(instance=profile)
    return render(request, 'alumni/profile.html', {'form': form, 'profile': profile})

@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('alumni:profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'alumni/profile.html', {'form': form, 'profile': request.user.profile})

@login_required
def profile_view(request):
    profile = request.user.alumniprofile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('alumni:profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'alumni/profile.html', {'form': form, 'profile': profile})

@login_required
def job_list(request):
    jobs = Job.objects.filter(is_active=True).order_by('-posted_date')
    return render(request, 'alumni/job_list.html', {'jobs': jobs})

@login_required
def job_create(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user.alumniprofile
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('alumni:job_list')
    else:
        form = JobForm()
    return render(request, 'alumni/job_form.html', {'form': form})

@login_required
def event_list(request):
    events = Event.objects.all().order_by('-date')
    now = timezone.localtime(timezone.now())
    cutoff_time = now - timedelta(hours=96)
    
    events = Event.objects.filter(
        models.Q(date__gte=cutoff_time) |
        models.Q(date__gte=now)
    ).order_by('-date')
    
    for event in events:
        event.attending_count = event.eventattendance_set.filter(status='YES').count()
        event.maybe_count = event.eventattendance_set.filter(status='MAYBE').count()
        event.not_attending_count = event.eventattendance_set.filter(status='NO').count()

        # Convert UTC to IST by adding 5 hours and 30 minutes
        ist_offset = timedelta(hours=5, minutes=30)
        start_time = timezone.localtime(event.date) + ist_offset
        end_time = start_time + timedelta(hours=3)
        now_ist = now + ist_offset
        
        if start_time <= now_ist <= end_time:
            event.status = 'going'
        elif start_time > now_ist:
            event.status = 'upcoming'
        else:
            event.status = 'past'
    
    context = {
        'events': events,
        'now': now_ist,
    }
    return render(request, 'alumni/event_list.html', context)

@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.is_approved = request.user.is_staff  # Auto-approve if admin creates
            event.save()
            if request.user.is_staff:
                messages.success(request, 'Event created successfully!')
            else:
                messages.success(request, 'Event submitted for approval. An admin will review it shortly.')
            return redirect('alumni:event_list')
    else:
        form = EventForm()
    
    return render(request, 'alumni/event_form.html', {'form': form})

@login_required
def success_story_create(request):
    if request.method == 'POST':
        form = SuccessStoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.alumni = request.user.alumniprofile
            story.is_approved = False  # Set to False by default
            
            if 'image' in request.FILES:
                story.image = request.FILES['image']
                
            story.save()
            messages.success(request, 'Success story submitted for approval. An admin will review it shortly.')
            return redirect('alumni:success_story_list')
    else:
        form = SuccessStoryForm()
    return render(request, 'alumni/success_story_form.html', {'form': form})

# Add this new view for admin approval
@user_passes_test(lambda u: u.is_staff)
def approve_success_story(request, story_id):
    if request.method == 'POST':
        story = get_object_or_404(SuccessStory, id=story_id)
        action = request.POST.get('action')
        
        if action == 'approve':
            story.is_approved = True
            story.save()
            messages.success(request, 'Success story approved!')
        elif action == 'reject':
            story.delete()
            messages.success(request, 'Success story rejected and removed.')
            
    return redirect('alumni:admin_dashboard')

@login_required
def like_story(request, story_id):
    story = get_object_or_404(SuccessStory, id=story_id)
    like, created = StoryLike.objects.get_or_create(
        story=story,
        user=request.user
    )
    
    if not created:
        # Unlike if already liked
        like.delete()
    
    return JsonResponse({
        'like_count': story.likes.count()
    })

    
    return JsonResponse({
        'user_name': request.user.get_full_name(),
        'content': comment.content,
        'created_at': comment.created_at.isoformat()
    })

@login_required
def success_story_list(request):
    stories = SuccessStory.objects.filter(is_approved=True).order_by('-date_posted')
    for story in stories:
        story.user_has_liked = story.likes.filter(id=request.user.id).exists()
    return render(request, 'alumni/success_story_list.html', {
        'success_stories': stories,
    })

@login_required
def add_comment(request, pk):
    story = get_object_or_404(SuccessStory, pk=pk)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Get the raw content directly from the request
            content = data.get('content')
            
            if not content:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Comment cannot be empty'
                }, status=400)

            # Create the comment with raw content
            comment = StoryComment.objects.create(
                story=story,
                user=request.user,
                content=content
            )
            
            # Return the raw content directly
            return JsonResponse({
                'status': 'success',
                'comment_id': comment.id,
                'user_name': request.user.get_full_name(),
                'content': content,
                'created_at': 'just now'
            }, encoder=json.JSONEncoder)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(StoryComment, id=comment_id, user=request.user)
    if request.method == 'POST':
        comment.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def like_story(request, pk):
    story = get_object_or_404(SuccessStory, pk=pk)
    if request.method == 'POST':
        if story.likes.filter(id=request.user.id).exists():
            story.likes.remove(request.user)
            liked = False
        else:
            story.likes.add(request.user)
            liked = True
        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'like_count': story.likes.count()
        })
    return JsonResponse({'status': 'error'}, status=400)



@login_required
def mentorship_list(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.alumniprofile.is_mentor:
        mentor_requests = MentorshipRequest.objects.filter(
            mentor=request.user.alumniprofile
        ).select_related('mentee__user', 'mentor__user')
    else:
        mentor_requests = MentorshipRequest.objects.filter(
            mentee=request.user.alumniprofile
        ).select_related('mentee__user', 'mentor__user')

    mentors = AlumniProfile.objects.filter(is_mentor=True)

    department = request.GET.get('department')
    if department:
        mentors = mentors.filter(department__icontains=department)
    
    context = {
        'mentors': mentors,
        'mentor_requests': mentor_requests  # Fixed: Pass the correct mentor_requests queryset
    }
    return render(request, 'alumni/mentorship_list.html', context)

# @login_required
# def mentorship_request(request, mentor_id):
#     mentor = get_object_or_404(AlumniProfile, id=mentor_id, is_mentor=True)
#     if request.method == 'POST':
#         form = MentorshipRequestForm(request.POST)
#         if form.is_valid():
#             mentorship = form.save(commit=False)
#             mentorship.mentor = mentor
#             mentorship.mentee = request.user.alumniprofile
#             mentorship.save()
#             messages.success(request, 'Mentorship request sent successfully!')
#             return redirect('alumni:mentorship_list')
#     return redirect('alumni:mentorship_list')
def mentorship_request(request, mentor_id):
    mentor = get_object_or_404(AlumniProfile, id=mentor_id, is_mentor=True)
    mentee_profile = request.user.alumniprofile

    # Check for existing request with status PENDING or ACCEPTED
    existing_request = MentorshipRequest.objects.filter(
        mentor=mentor,
        mentee=mentee_profile,
        status__in=['PENDING', 'ACCEPTED']
    ).first()

    if existing_request:
        messages.error(request, "You have already sent a request to this mentor or are currently being mentored.")
        return redirect('alumni:mentorship_list')

    if request.method == 'POST':
        form = MentorshipRequestForm(request.POST)
        if form.is_valid():
            mentorship = form.save(commit=False)
            mentorship.mentor = mentor
            mentorship.mentee = mentee_profile
            mentorship.save()
            messages.success(request, 'Mentorship request sent successfully!')
            return redirect('alumni:mentorship_list')

    messages.error(request, 'Something went wrong. Please try again.')
    return redirect('alumni:mentorship_list')


@login_required
def event_rsvp(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['YES', 'NO', 'MAYBE']:
            EventAttendance.objects.update_or_create(
                event=event,
                alumni=request.user.alumniprofile,
                defaults={'status': status}
            )
            messages.success(request, 'RSVP updated successfully!')
        else:
            messages.error(request, 'Invalid RSVP status.')
    return redirect('alumni:event_list')


@login_required
def mentorship_response(request, request_id):
    mentorship_request = get_object_or_404(MentorshipRequest, id=request_id, mentor=request.user.alumniprofile)
    if request.method == 'POST':
        action = request.POST.get('action')
        student_name = mentorship_request.mentee.user.get_full_name()
        
        if action == 'accept':
            mentorship_request.status = 'ACCEPTED'
            messages.success(request, f'You have accepted {student_name}\'s mentorship request!')
        elif action == 'reject':
            mentorship_request.status = 'REJECTED'
            reject_reason = request.POST.get('reject_reason', '')
            if reject_reason:
                messages.error(request, f'You have cancelled the mentorship with {student_name}.')
            else:
                messages.error(request, f'You have declined {student_name}\'s mentorship request.')
        
        mentorship_request.save()
    return redirect('alumni:mentorship_list')


@login_required
def clear_mentorship_requests(request):
    if request.method == 'POST':
        # Delete all requests where the user is the mentee
        MentorshipRequest.objects.filter(mentee=request.user.alumniprofile).delete()
        messages.success(request, 'All mentorship requests have been cleared.')
    return redirect('alumni:mentorship_list')


@login_required
def all_success_stories(request):
    all_stories = SuccessStory.objects.filter(is_approved=True).order_by('-date_posted')
    return render(request, 'alumni/all_success_stories.html', {
        'all_stories': all_stories,
    })


from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Job, JobApplication

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        if not JobApplication.objects.filter(job=job, applicant=request.user.alumniprofile).exists():
            JobApplication.objects.create(job=job, applicant=request.user.alumniprofile)
            messages.success(request, 'Successfully applied for the job!')
        else:
            messages.info(request, 'You have already applied for this job.')
    return redirect('alumni:job_detail', job_id)

@login_required
def my_applications(request):
    applications = JobApplication.objects.filter(
        applicant=request.user.alumniprofile
    ).select_related('job', 'job__posted_by').order_by('-applied_date')
    
    return render(request, 'alumni/my_applications.html', {
        'applications': applications
    })

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    has_applied = False
    if request.user.is_authenticated:
        has_applied = JobApplication.objects.filter(
            job=job, 
            applicant=request.user.alumniprofile
        ).exists()
    return render(request, 'alumni/job_detail.html', {
        'job': job,
        'has_applied': has_applied,
        'current_date':date.today()
    })


from django.contrib.auth.decorators import user_passes_test
from datetime import date
from .models import Event, MentorshipRequest, AlumniProfile

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    pending_events = Event.objects.filter(is_approved=False).order_by('-date')
    pending_stories = SuccessStory.objects.filter(is_approved=False).order_by('-date_posted')
    mentorship_pairs = MentorshipRequest.objects.filter(status='ACCEPTED').select_related(
        'mentor__user', 'mentee__user'
    )
    
    # Count total alumni excluding students
    total_alumni = AlumniProfile.objects.exclude(
        Q(current_job__icontains='student') |
        Q(designation__icontains='student')
    ).count()
    
    context = {
        'pending_events': pending_events,
        'pending_stories': pending_stories,  # Add this line
        'mentorship_pairs': mentorship_pairs,
        'total_events': Event.objects.count(),
        'total_mentorships': mentorship_pairs.count(),
        'total_alumni': total_alumni,
    }
    return render(request, 'alumni/admin/dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def approve_event(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        action = request.POST.get('action')
        
        if action == 'approve':
            event.is_approved = True
            event.save()
            messages.success(request, 'Event approved successfully!')
        elif action == 'reject':
            event.delete()
            messages.success(request, 'Event rejected and removed.')
            
    return redirect('alumni:admin_dashboard')


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('alumni:admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials')
    
    return render(request, 'alumni/admin/login.html')


@login_required
@admin_required
def admin_alumni_list(request):
    alumni_list = AlumniProfile.objects.filter(
        user__is_active=True
    ).filter(
        Q(current_job__icontains='teacher') |
        Q(designation__icontains='teacher') |
        Q(current_job__icontains='professor') |
        # Add more specific professional terms
        Q(current_job__icontains='engineer') |
        Q(current_job__icontains='developer') |
        Q(current_job__icontains='manager') |
        Q(current_job__icontains='professional') |
        Q(designation__icontains='professional') |
        # Include those with company info who are not students
        Q(company__isnull=False) |
        Q(designation__isnull=False)
    ).exclude(
        Q(current_job__icontains='student') |
        Q(designation__icontains='student')
    ).select_related('user')
    
    context = {
        'alumni_list': alumni_list
    }
    return render(request, 'alumni/admin/alumni_list.html', context)
