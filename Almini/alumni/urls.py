from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include


app_name = 'alumni'


urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', auth_views.LogoutView.as_view(next_page='alumni:home'), name='logout'),  # Add this line
    path('register/', views.register, name='register'),  # Add this line
    path('profile/', views.profile_view, name='profile'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/create/', views.job_create, name='job_create'),
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:event_id>/rsvp/', views.event_rsvp, name='event_rsvp'),
    path('success-stories/', views.success_story_list, name='success_story_list'),
    path('success-stories/create/', views.success_story_create, name='success_story_create'),
    # path change
    path('success-stories/all/', views.all_success_stories, name='all_success_stories'),
    # path('success-stories/all/', views.all_success_stories, name='all_success_stories'),
    path('mentorship/', views.mentorship_list, name='mentorship_list'),
    path('mentorship/<int:mentor_id>/request/', views.mentorship_request, name='mentorship_request'),
    path('mentorship/<int:request_id>/response/', views.mentorship_response, name='mentorship_response'),
    path('mentorship/clear/', views.clear_mentorship_requests, name='clear_mentorship_requests'),
    path('success-stories/<int:pk>/like/', views.like_story, name='like_story'),
    path('success-stories/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('success-stories/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    
    #  admin dashboard 
    
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'), 
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/admin/login/', views.admin_login, name='admin_login'),
    path('dashboard/admin/alumni/', views.admin_alumni_list, name='admin_alumni_list'),
    path('dashboard/admin/approve-event/<int:event_id>/', views.approve_event, name='approve_event'),
    path('success-story/<int:story_id>/approve/', views.approve_success_story, name='approve_success_story'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)