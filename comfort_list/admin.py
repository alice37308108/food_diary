from django.contrib import admin
from .models import Category, ComfortAction, ActionExecution, HappinessRecord

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['emoji', 'display_name', 'name']
    list_filter = ['name']

@admin.register(ComfortAction)
class ComfortActionAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'user', 'estimated_minutes', 'is_favorite', 'created_at']
    list_filter = ['category', 'is_favorite', 'created_at']
    search_fields = ['name', 'description']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(ActionExecution)
class ActionExecutionAdmin(admin.ModelAdmin):
    list_display = ['action', 'executed_at', 'comfort_level', 'memo']
    list_filter = ['executed_at', 'comfort_level', 'action__category']
    search_fields = ['action__name', 'memo']
    date_hierarchy = 'executed_at'

@admin.register(HappinessRecord)
class HappinessRecordAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'recorded_at', 'has_photo']
    list_filter = ['recorded_at', 'user']
    search_fields = ['title', 'content']
    date_hierarchy = 'recorded_at'
    
    def has_photo(self, obj):
        return bool(obj.photo)
    has_photo.boolean = True
    has_photo.short_description = '写真'
