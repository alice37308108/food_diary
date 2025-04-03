from django.contrib import admin
from .models import VitaminIntake

@admin.register(VitaminIntake)
class VitaminIntakeAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'intake_count', 'daily_goal', 'get_progress_percentage')
    list_filter = ('date', 'user')
    search_fields = ('user__username',)
    date_hierarchy = 'date'