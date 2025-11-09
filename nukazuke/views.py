from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import os
import requests
import json
from .models import PickledVegetable


def index(request):
    """ぬか漬け管理のメインページ"""
    # 現在漬けている野菜
    pickled_vegetables = PickledVegetable.objects.filter(removed_at__isnull=True)
    
    # 最近取り出した野菜（過去7日間）
    week_ago = timezone.now() - timezone.timedelta(days=7)
    recent_removed = PickledVegetable.objects.filter(
        removed_at__isnull=False,
        removed_at__gte=week_ago
    )[:10]
    
    context = {
        'pickled_vegetables': pickled_vegetables,
        'recent_removed': recent_removed,
        'vegetable_choices': PickledVegetable.VEGETABLE_CHOICES,
    }
    return render(request, 'nukazuke/index.html', context)


@require_POST
def pickle_vegetable(request):
    """野菜を漬ける"""
    vegetable_type = request.POST.get('vegetable_type')
    custom_name = request.POST.get('custom_name', '').strip()
    
    if not vegetable_type:
        messages.error(request, '野菜の種類を選択してください。')
        return redirect('nukazuke:index')
    
    # 新しいぬか漬けを作成
    pickled_vegetable = PickledVegetable.objects.create(
        vegetable_type=vegetable_type,
        custom_name=custom_name if custom_name else None
    )
    
    # リマインドタスクをスケジュール（後で実装）
    # schedule_reminder_task(pickled_vegetable.id)
    
    messages.success(request, f'{pickled_vegetable.display_name}を漬けました！24時間後にリマインドします。')
    return redirect('nukazuke:index')


@require_POST
def remove_vegetable(request, vegetable_id):
    """野菜を取り出す"""
    vegetable = get_object_or_404(PickledVegetable, id=vegetable_id, removed_at__isnull=True)
    
    # 取り出し時刻を記録
    vegetable.removed_at = timezone.now()
    vegetable.save()
    
    # リマインドタスクをキャンセル（後で実装）
    # cancel_reminder_task(vegetable_id)
    
    hours = round(vegetable.hours_pickled, 1)
    messages.success(request, f'{vegetable.display_name}を取り出しました！（{hours}時間漬けていました）')
    return redirect('nukazuke:index')


def send_line_message(vegetable_id):
    """LINEメッセージを送信"""
    try:
        vegetable = PickledVegetable.objects.get(id=vegetable_id, removed_at__isnull=True)
        
        # 経過時間を計算
        hours_elapsed = vegetable.hours_pickled
        
        # メッセージを取得
        message = vegetable.get_reminder_message(hours_elapsed)
        if not message:
            return False
        
        # LINE API設定
        access_token = os.getenv("LINE_ACCESS_TOKEN")
        user_id = os.getenv("LINE_USER_ID")
        
        if not access_token or not user_id:
            print("LINE_ACCESS_TOKEN or LINE_USER_ID not found in environment variables")
            return False
        
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "to": user_id,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            # 送信フラグを更新
            if hours_elapsed >= 72:
                vegetable.reminder_72h_sent = True
            elif hours_elapsed >= 48:
                vegetable.reminder_48h_sent = True
            elif hours_elapsed >= 24:
                vegetable.reminder_24h_sent = True
            vegetable.save()
            return True
        else:
            print(f"LINE API Error: {response.status_code}, {response.text}")
            return False
            
    except PickledVegetable.DoesNotExist:
        print(f"Vegetable with id {vegetable_id} not found or already removed")
        return False
    except Exception as e:
        print(f"Error sending LINE message: {e}")
        return False


@csrf_exempt
def test_line_message(request):
    """LINEメッセージのテスト送信（開発用）"""
    if request.method == 'POST':
        vegetable_id = request.POST.get('vegetable_id')
        if vegetable_id:
            success = send_line_message(vegetable_id)
            return JsonResponse({
                'success': success,
                'message': 'メッセージを送信しました' if success else 'メッセージの送信に失敗しました'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def history(request):
    """ぬか漬け履歴ページ"""
    vegetables = PickledVegetable.objects.all()
    
    context = {
        'vegetables': vegetables,
    }
    return render(request, 'nukazuke/history.html', context)