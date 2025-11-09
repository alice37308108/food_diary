from django.contrib import admin
from .models import PickledVegetable


@admin.register(PickledVegetable)
class PickledVegetableAdmin(admin.ModelAdmin):
    list_display = [
        'display_name', 
        'vegetable_type', 
        'pickled_at', 
        'removed_at', 
        'hours_pickled_display',
        'is_pickled_display',
        'reminder_status'
    ]
    list_filter = [
        'vegetable_type', 
        'reminder_24h_sent',
        'reminder_48h_sent',
        'reminder_72h_sent',
        'pickled_at'
    ]
    search_fields = ['custom_name', 'vegetable_type']
    readonly_fields = ['hours_pickled_display', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('vegetable_type', 'custom_name')
        }),
        ('日時情報', {
            'fields': ('pickled_at', 'removed_at', 'hours_pickled_display')
        }),
        ('リマインド状況', {
            'fields': ('reminder_24h_sent', 'reminder_48h_sent', 'reminder_72h_sent')
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def hours_pickled_display(self, obj):
        """経過時間の表示用"""
        return f"{obj.hours_pickled:.1f}時間"
    hours_pickled_display.short_description = '経過時間'
    
    def is_pickled_display(self, obj):
        """漬け状態の表示用"""
        return "漬け中" if obj.is_pickled else "取り出し済み"
    is_pickled_display.short_description = '状態'
    is_pickled_display.boolean = True
    
    def reminder_status(self, obj):
        """リマインド状況の表示"""
        if obj.reminder_72h_sent:
            return "72h送信済み"
        elif obj.reminder_48h_sent:
            return "48h送信済み"
        elif obj.reminder_24h_sent:
            return "24h送信済み"
        else:
            return "未送信"
    reminder_status.short_description = 'リマインド状況'
    
    actions = ['mark_as_removed', 'reset_reminders']
    
    def mark_as_removed(self, request, queryset):
        """選択した野菜を取り出し済みにする"""
        from django.utils import timezone
        updated = queryset.filter(removed_at__isnull=True).update(removed_at=timezone.now())
        self.message_user(request, f'{updated}個の野菜を取り出し済みにしました。')
    mark_as_removed.short_description = '選択した野菜を取り出し済みにする'
    
    def reset_reminders(self, request, queryset):
        """リマインド送信フラグをリセット"""
        updated = queryset.update(
            reminder_24h_sent=False,
            reminder_48h_sent=False,
            reminder_72h_sent=False
        )
        self.message_user(request, f'{updated}個の野菜のリマインドフラグをリセットしました。')
    reset_reminders.short_description = 'リマインドフラグをリセット'