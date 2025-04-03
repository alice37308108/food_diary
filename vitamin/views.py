from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import VitaminIntake

@login_required
def home(request):
    # 現在のローカル日時を取得（タイムゾーンを考慮）
    today = timezone.localtime(timezone.now()).date()

    # 今日の記録を取得または作成
    intake, created = VitaminIntake.objects.get_or_create(
        user=request.user,
        date=today,
        defaults={'daily_goal': 10}
    )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'increment':
            intake.intake_count = min(intake.intake_count + 1, intake.daily_goal)
            intake.save()
            messages.success(request, "ビタミンCの摂取を記録しました！")

        elif action == 'decrement':
            intake.intake_count = max(0, intake.intake_count - 1)
            intake.save()
            messages.info(request, "ビタミンCの摂取を1つ減らしました。")

        elif action == 'reset':
            intake.intake_count = 0
            intake.save()
            messages.warning(request, "今日の記録をリセットしました。")

        elif action == 'update_goal':
            new_goal = request.POST.get('daily_goal')
            try:
                intake.daily_goal = int(new_goal)
                intake.save()
                messages.success(request, f"目標を{new_goal}杯に更新しました！")
            except ValueError:
                messages.error(request, "有効な数値を入力してください。")

        return redirect('vitamin:home')

    # 時間帯に基づく目標計算（タイムゾーンを考慮）
    current_hour = timezone.localtime(timezone.now()).hour
    if current_hour >= 6 and current_hour < 12:
        time_goal = int(intake.daily_goal * 0.3)  # 朝 30%
    elif current_hour >= 12 and current_hour < 18:
        time_goal = int(intake.daily_goal * 0.7)  # 昼 70%
    elif current_hour >= 18 and current_hour < 22:
        time_goal = int(intake.daily_goal * 0.9)  # 夕方 90%
    else:
        time_goal = intake.daily_goal  # 夜 100%

    # 提案スケジュール
    schedule = [
        {"時間帯": "朝食時 (6-9時)", "目標": int(intake.daily_goal * 0.2)},
        {"時間帯": "午前中 (9-12時)", "目標": int(intake.daily_goal * 0.1)},
        {"時間帯": "昼食時 (12-14時)", "目標": int(intake.daily_goal * 0.2)},
        {"時間帯": "午後 (14-18時)", "目標": int(intake.daily_goal * 0.2)},
        {"時間帯": "夕食時 (18-20時)", "目標": int(intake.daily_goal * 0.2)},
        {"時間帯": "夜 (20-22時)", "目標": int(intake.daily_goal * 0.1)},
    ]

    context = {
        'intake': intake,
        'progress': intake.get_progress_percentage(),
        'time_goal': time_goal,
        'is_on_track': intake.intake_count >= time_goal,
        'schedule': schedule,
        'today': today,  # 今日の日付をコンテキストに追加
    }

    return render(request, 'vitamin/home.html', context)


@login_required
def history(request):
    # 過去7日間の記録を取得（タイムゾーンを考慮）
    end_date = timezone.localtime(timezone.now()).date()
    start_date = end_date - timedelta(days=6)
    date_range = [start_date + timedelta(days=i) for i in range(7)]

    intakes = []
    for date in date_range:
        intake, created = VitaminIntake.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={'daily_goal': 10}
        )
        intakes.append(intake)

    context = {
        'intakes': intakes,
        'today': end_date,  # 今日の日付をコンテキストに追加
    }

    return render(request, 'vitamin/history.html', context)