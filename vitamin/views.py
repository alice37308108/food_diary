from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import VitaminIntake


@login_required
def home(request):
    # 現在のローカル日時を取得（タイムゾーンを考慮）
    today = timezone.localtime(timezone.now()).date()
    current_hour = timezone.localtime(timezone.now()).hour

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

    # 時間帯に基づく目標計算（個別の時間帯目標）
    if current_hour >= 6 and current_hour < 9:
        current_period_goal = int(intake.daily_goal * 0.2)  # 朝食時 20%
        time_period = "朝食時（6-9時）"
    elif current_hour >= 9 and current_hour < 12:
        current_period_goal = int(intake.daily_goal * 0.1)  # 午前中 10%
        time_period = "午前中（9-12時）"
    elif current_hour >= 12 and current_hour < 14:
        current_period_goal = int(intake.daily_goal * 0.2)  # 昼食時 20%
        time_period = "昼食時（12-14時）"
    elif current_hour >= 14 and current_hour < 18:
        current_period_goal = int(intake.daily_goal * 0.2)  # 午後 20%
        time_period = "午後（14-18時）"
    elif current_hour >= 18 and current_hour < 20:
        current_period_goal = int(intake.daily_goal * 0.2)  # 夕食時 20%
        time_period = "夕食時（18-20時）"
    elif current_hour >= 20 and current_hour < 22:
        current_period_goal = int(intake.daily_goal * 0.1)  # 夜 10%
        time_period = "夜（20-22時）"
    else:
        current_period_goal = 0  # 深夜は追加摂取なし
        time_period = "深夜/早朝（22-6時）"

    # 現在の時間帯までの累計目標（これまでの時間帯も含む）
    if current_hour >= 6 and current_hour < 9:
        cumulative_goal = int(intake.daily_goal * 0.2)  # 朝食時まで
    elif current_hour >= 9 and current_hour < 12:
        cumulative_goal = int(intake.daily_goal * 0.3)  # 午前中まで
    elif current_hour >= 12 and current_hour < 14:
        cumulative_goal = int(intake.daily_goal * 0.5)  # 昼食時まで
    elif current_hour >= 14 and current_hour < 18:
        cumulative_goal = int(intake.daily_goal * 0.7)  # 午後まで
    elif current_hour >= 18 and current_hour < 20:
        cumulative_goal = int(intake.daily_goal * 0.9)  # 夕食時まで
    elif current_hour >= 20:
        cumulative_goal = intake.daily_goal  # 夜以降は全て
    else:
        cumulative_goal = 0  # 深夜は摂取なし

    # 現在時刻までに摂取すべき量と実際の摂取量の差を計算
    remaining_for_period = max(0, current_period_goal)
    remaining_for_cumulative = max(0, cumulative_goal - intake.intake_count)

    # 提案スケジュール
    schedule = [
        {"時間帯": "朝食時 (6-9時)", "目標": int(intake.daily_goal * 0.2), "残り": max(0,
                                                                                       int(intake.daily_goal * 0.2) - (
                                                                                           intake.intake_count if current_hour >= 6 and current_hour < 9 else 0))},
        {"時間帯": "午前中 (9-12時)", "目標": int(intake.daily_goal * 0.1), "残り": max(0,
                                                                                        int(intake.daily_goal * 0.1) - (
                                                                                            intake.intake_count if current_hour >= 9 and current_hour < 12 else 0))},
        {"時間帯": "昼食時 (12-14時)", "目標": int(intake.daily_goal * 0.2), "残り": max(0,
                                                                                         int(intake.daily_goal * 0.2) - (
                                                                                             intake.intake_count if current_hour >= 12 and current_hour < 14 else 0))},
        {"時間帯": "午後 (14-18時)", "目標": int(intake.daily_goal * 0.2), "残り": max(0,
                                                                                       int(intake.daily_goal * 0.2) - (
                                                                                           intake.intake_count if current_hour >= 14 and current_hour < 18 else 0))},
        {"時間帯": "夕食時 (18-20時)", "目標": int(intake.daily_goal * 0.2), "残り": max(0,
                                                                                         int(intake.daily_goal * 0.2) - (
                                                                                             intake.intake_count if current_hour >= 18 and current_hour < 20 else 0))},
        {"時間帯": "夜 (20-22時)", "目標": int(intake.daily_goal * 0.1), "残り": max(0, int(intake.daily_goal * 0.1) - (
            intake.intake_count if current_hour >= 20 and current_hour < 22 else 0))},
    ]

    context = {
        'intake': intake,
        'progress': intake.get_progress_percentage(),
        'current_period_goal': current_period_goal,
        'time_period': time_period,
        'cumulative_goal': cumulative_goal,
        'remaining_for_period': remaining_for_period,
        'remaining_for_cumulative': remaining_for_cumulative,
        'is_on_track': intake.intake_count >= cumulative_goal,
        'schedule': schedule,
        'today': today,
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
        'today': end_date,
    }

    return render(request, 'vitamin/history.html', context)
