from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import os
import requests
import json
from .models import PickledVegetable, VegetableType


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
    
    # 有効な野菜タイプを取得
    vegetable_types = VegetableType.objects.filter(is_active=True)
    
    context = {
        'pickled_vegetables': pickled_vegetables,
        'recent_removed': recent_removed,
        'vegetable_types': vegetable_types,
    }
    return render(request, 'nukazuke/index.html', context)


@require_POST
def pickle_vegetable(request):
    """野菜を漬ける"""
    vegetable_type_id = request.POST.get('vegetable_type')
    custom_name = request.POST.get('custom_name', '').strip()
    
    if not vegetable_type_id:
        messages.error(request, '野菜の種類を選択してください。')
        return redirect('nukazuke:index')
    
    try:
        vegetable_type = VegetableType.objects.get(id=vegetable_type_id)
    except VegetableType.DoesNotExist:
        messages.error(request, '選択された野菜の種類が見つかりません。')
        return redirect('nukazuke:index')
    
    # 新しいぬか漬けを作成
    pickled_vegetable = PickledVegetable.objects.create(
        vegetable_type=vegetable_type,
        custom_name=custom_name if custom_name else None
    )
    
    # リマインドタスクをスケジュール（後で実装）
    # schedule_reminder_task(pickled_vegetable.id)
    
    # 漬けた時にもLINEメッセージを送信
    pickle_message = f"{pickled_vegetable.vegetable_emoji} {pickled_vegetable.simple_display_name}を漬けました！\n24時間後にリマインドしますので、お楽しみに〜"
    line_success = send_line_message_with_text(pickle_message)
    
    if line_success:
        messages.success(request, f'{pickled_vegetable.display_name}を漬けました！LINEにもお知らせしました。24時間後にリマインドします。')
    else:
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


def send_line_message_with_text(message_text):
    """カスタムテキストでLINEメッセージを送信"""
    try:
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
                    "text": message_text
                }
            ]
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            return True
        else:
            print(f"LINE API Error: {response.status_code}, {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending LINE message: {e}")
        return False


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
            try:
                vegetable = PickledVegetable.objects.get(id=vegetable_id)
                # テスト用のメッセージを送信
                test_message = f"🧪 テスト送信\n{vegetable.simple_display_name}のリマインドメッセージをテストしています！\n\n実際のメッセージ:\n{vegetable.get_reminder_message(vegetable.hours_pickled)}"
                success = send_line_message_with_text(test_message)
                return JsonResponse({
                    'success': success,
                    'message': 'テストメッセージを送信しました！' if success else 'メッセージの送信に失敗しました'
                })
            except PickledVegetable.DoesNotExist:
                return JsonResponse({'success': False, 'message': '野菜が見つかりません'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'エラーが発生しました: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def history(request):
    """ぬか漬け履歴ページ"""
    vegetables = PickledVegetable.objects.all()
    completed_count = PickledVegetable.objects.filter(removed_at__isnull=False).count()
    
    context = {
        'vegetables': vegetables,
        'completed_count': completed_count,
    }
    return render(request, 'nukazuke/history.html', context)


@require_POST
def delete_history(request, vegetable_id):
    """履歴を個別削除"""
    vegetable = get_object_or_404(PickledVegetable, id=vegetable_id)
    
    name = vegetable.display_name
    vegetable.delete()
    
    messages.success(request, f'{name}の履歴を削除しました。')
    return redirect('nukazuke:history')


@require_POST
def delete_all_history(request):
    """全履歴を削除"""
    count = PickledVegetable.objects.count()
    PickledVegetable.objects.all().delete()
    
    messages.success(request, f'{count}件の履歴をすべて削除しました。')
    return redirect('nukazuke:history')


@require_POST
def delete_completed_history(request):
    """完了した履歴のみ削除"""
    count = PickledVegetable.objects.filter(removed_at__isnull=False).count()
    PickledVegetable.objects.filter(removed_at__isnull=False).delete()
    
    messages.success(request, f'{count}件の完了済み履歴を削除しました。')
    return redirect('nukazuke:history')


def manage_vegetables(request):
    """野菜タイプ管理ページ"""
    vegetable_types = VegetableType.objects.all()
    
    context = {
        'vegetable_types': vegetable_types,
    }
    return render(request, 'nukazuke/manage_vegetables.html', context)


@require_POST
def add_vegetable_type(request):
    """野菜タイプを追加"""
    name = request.POST.get('name', '').strip()
    emoji = request.POST.get('emoji', '🥗').strip()
    
    if not name:
        messages.error(request, '野菜名を入力してください。')
        return redirect('nukazuke:manage_vegetables')
    
    if VegetableType.objects.filter(name=name).exists():
        messages.error(request, 'この野菜名は既に登録されています。')
        return redirect('nukazuke:manage_vegetables')
    
    VegetableType.objects.create(name=name, emoji=emoji)
    messages.success(request, f'{emoji} {name}を追加しました！')
    return redirect('nukazuke:manage_vegetables')


@require_POST
def edit_vegetable_type(request, vegetable_type_id):
    """野菜タイプを編集"""
    vegetable_type = get_object_or_404(VegetableType, id=vegetable_type_id)
    
    name = request.POST.get('name', '').strip()
    emoji = request.POST.get('emoji', '🥗').strip()
    is_active = request.POST.get('is_active') == 'on'
    
    if not name:
        messages.error(request, '野菜名を入力してください。')
        return redirect('nukazuke:manage_vegetables')
    
    # 同じ名前の他の野菜がないかチェック
    if VegetableType.objects.filter(name=name).exclude(id=vegetable_type_id).exists():
        messages.error(request, 'この野菜名は既に登録されています。')
        return redirect('nukazuke:manage_vegetables')
    
    vegetable_type.name = name
    vegetable_type.emoji = emoji
    vegetable_type.is_active = is_active
    vegetable_type.save()
    
    messages.success(request, f'{emoji} {name}を更新しました！')
    return redirect('nukazuke:manage_vegetables')


@require_POST
def delete_vegetable_type(request, vegetable_type_id):
    """野菜タイプを削除"""
    vegetable_type = get_object_or_404(VegetableType, id=vegetable_type_id)
    
    # 使用中の野菜タイプは削除できない
    if PickledVegetable.objects.filter(vegetable_type=vegetable_type).exists():
        messages.error(request, 'この野菜タイプは使用中のため削除できません。無効化してください。')
        return redirect('nukazuke:manage_vegetables')
    
    name = vegetable_type.name
    emoji = vegetable_type.emoji
    vegetable_type.delete()
    
    messages.success(request, f'{emoji} {name}を削除しました。')
    return redirect('nukazuke:manage_vegetables')