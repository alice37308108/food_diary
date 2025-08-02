from django.contrib import admin
from .models import Category, ComfortAction, ActionExecution, HappinessRecord

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['emoji', 'display_name', 'name']
    list_filter = ['name']

@admin.register(ComfortAction)
class ComfortActionAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_categories', 'user', 'estimated_minutes', 'is_favorite', 'created_at']
    list_filter = ['categories', 'is_favorite', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['categories']  # ManyToManyFieldの編集を簡単にする
    
    def get_categories(self, obj):
        return ', '.join([cat.display_name for cat in obj.categories.all()])
    get_categories.short_description = 'カテゴリ'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(ActionExecution)
class ActionExecutionAdmin(admin.ModelAdmin):
    list_display = ['action', 'executed_at', 'comfort_level', 'memo']
    list_filter = ['executed_at', 'comfort_level', 'action__categories']
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
