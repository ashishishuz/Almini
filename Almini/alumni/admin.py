from django.contrib import admin
from .models import AlumniProfile, Job, Event, EventAttendance, SuccessStory, MentorshipRequest

@admin.register(AlumniProfile)
class AlumniProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'graduation_year', 'department', 'current_job', 'company', 'location', 'is_mentor')
    list_filter = ('graduation_year', 'department', 'is_mentor')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department', 'company')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'location', 'posted_date', 'is_active']
    list_filter = ['is_active', 'job_type', 'company_name', 'stream']
    search_fields = ['title', 'company_name', 'description', 'location']
    date_hierarchy = 'posted_date'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'created_by')
    list_filter = ('date', 'location')
    search_fields = ('title', 'description')
    date_hierarchy = 'date'

@admin.register(EventAttendance)
class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'alumni', 'status')
    list_filter = ('status', 'event')
    search_fields = ('event__title', 'alumni__user__username')

@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'alumni', 'date_posted', 'is_approved')
    list_filter = ('is_approved', 'date_posted')
    search_fields = ('title', 'content', 'alumni__user__username')
    date_hierarchy = 'date_posted'
    actions = ['approve_stories', 'unapprove_stories']

    def approve_stories(self, request, queryset):
        queryset.update(is_approved=True)
    approve_stories.short_description = "Approve selected stories"

    def unapprove_stories(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_stories.short_description = "Unapprove selected stories"

@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'mentee', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('mentor__user__username', 'mentee__user__username', 'message')
    date_hierarchy = 'created_at'
