from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView

from .models import VitaminIntake


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'vitamin/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 現在のローカル日時を取得（タイムゾーンを考慮）
        today = timezone.localtime(timezone.now()).date()
        current_hour = timezone.localtime(timezone.now()).hour

        # 今日の記録を取得または作成
        intake, created = VitaminIntake.objects.get_or_create(
            user=self.request.user,
            date=today,
            defaults={'daily_goal': 20}
        )

        # 時間帯に基づく目標計算（個別の時間帯目標）
        if current_hour >= 6 and current_hour < 9:
            current_period_goal = int(intake.daily_goal * 0.2)  # 朝食時 20%
            time_period = "朝食時（6-9時）"
        elif current_hour >= 9 and current_hour < 12:
            current_period_goal = int(intake.daily_goal * 0.15)  # 午前中 15%
            time_period = "午前中（9-12時）"
        elif current_hour >= 12 and current_hour < 14:
            current_period_goal = int(intake.daily_goal * 0.2)  # 昼食時 20%
            time_period = "昼食時（12-14時）"
        elif current_hour >= 14 and current_hour < 18:
            current_period_goal = int(intake.daily_goal * 0.15)  # 午後 15%
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
            cumulative_goal = int(intake.daily_goal * 0.35)  # 午前中まで (0.2 + 0.15)
        elif current_hour >= 12 and current_hour < 14:
            cumulative_goal = int(intake.daily_goal * 0.55)  # 昼食時まで (0.35 + 0.2)
        elif current_hour >= 14 and current_hour < 18:
            cumulative_goal = int(intake.daily_goal * 0.7)  # 午後まで (0.55 + 0.15)
        elif current_hour >= 18 and current_hour < 20:
            cumulative_goal = int(intake.daily_goal * 0.9)  # 夕食時まで (0.7 + 0.2)
        elif current_hour >= 20:
            cumulative_goal = intake.daily_goal  # 夜以降は全て
        else:
            cumulative_goal = 0  # 深夜は摂取なし

        # 現在時刻までに摂取すべき量と実際の摂取量の差を計算
        remaining_for_period = max(0, current_period_goal)
        remaining_for_cumulative = max(0, cumulative_goal - intake.intake_count)

        # 提案スケジュール作成
        schedule = []

        # 朝食時（6-9時）
        breakfast_goal = int(intake.daily_goal * 0.2)
        breakfast_remaining = breakfast_goal
        if current_hour >= 6:
            # 朝食時間内または過ぎている場合
            if current_hour < 9:
                # まだ朝食時間内
                breakfast_remaining = max(0, breakfast_goal - intake.intake_count)
            else:
                # 朝食時間を過ぎている場合は「達成済み」表示用に0にする
                breakfast_remaining = 0
        schedule.append({"時間帯": "朝食時 (6-9時)", "目標": breakfast_goal, "残り": breakfast_remaining})

        # 午前中（9-12時）
        morning_goal = int(intake.daily_goal * 0.15)
        morning_remaining = morning_goal
        if current_hour >= 9:
            # 午前中時間内または過ぎている場合
            morning_intake = intake.intake_count - (
                0 if breakfast_remaining == breakfast_goal else (breakfast_goal - breakfast_remaining))
            if current_hour < 12:
                # まだ午前中時間内
                morning_remaining = max(0, morning_goal - morning_intake)
            else:
                # 午前中時間を過ぎている場合は「達成済み」表示用に0にする
                morning_remaining = 0
        schedule.append({"時間帯": "午前中 (9-12時)", "目標": morning_goal, "残り": morning_remaining})

        # 昼食時（12-14時）
        lunch_goal = int(intake.daily_goal * 0.2)
        lunch_remaining = lunch_goal
        if current_hour >= 12:
            # 昼食時間内または過ぎている場合
            lunch_intake = intake.intake_count - (
                        breakfast_goal + morning_goal - (breakfast_remaining + morning_remaining))
            if current_hour < 14:
                # まだ昼食時間内
                lunch_remaining = max(0, lunch_goal - lunch_intake)
            else:
                # 昼食時間を過ぎている場合は「達成済み」表示用に0にする
                lunch_remaining = 0
        schedule.append({"時間帯": "昼食時 (12-14時)", "目標": lunch_goal, "残り": lunch_remaining})

        # 午後（14-18時）
        afternoon_goal = int(intake.daily_goal * 0.15)
        afternoon_remaining = afternoon_goal
        if current_hour >= 14:
            # 午後時間内または過ぎている場合
            afternoon_intake = intake.intake_count - (breakfast_goal + morning_goal + lunch_goal - (
                        breakfast_remaining + morning_remaining + lunch_remaining))
            if current_hour < 18:
                # まだ午後時間内
                afternoon_remaining = max(0, afternoon_goal - afternoon_intake)
            else:
                # 午後時間を過ぎている場合は「達成済み」表示用に0にする
                afternoon_remaining = 0
        schedule.append({"時間帯": "午後 (14-18時)", "目標": afternoon_goal, "残り": afternoon_remaining})

        # 夕食時（18-20時）
        dinner_goal = int(intake.daily_goal * 0.2)
        dinner_remaining = dinner_goal
        if current_hour >= 18:
            # 夕食時間内または過ぎている場合
            dinner_intake = intake.intake_count - (breakfast_goal + morning_goal + lunch_goal + afternoon_goal - (
                        breakfast_remaining + morning_remaining + lunch_remaining + afternoon_remaining))
            if current_hour < 20:
                # まだ夕食時間内
                dinner_remaining = max(0, dinner_goal - dinner_intake)
            else:
                # 夕食時間を過ぎている場合は「達成済み」表示用に0にする
                dinner_remaining = 0
        schedule.append({"時間帯": "夕食時 (18-20時)", "目標": dinner_goal, "残り": dinner_remaining})

        # 夜（20-22時）
        evening_goal = int(intake.daily_goal * 0.1)
        evening_remaining = evening_goal
        if current_hour >= 20:
            # 夜時間内または過ぎている場合
            evening_intake = intake.intake_count - (
                        breakfast_goal + morning_goal + lunch_goal + afternoon_goal + dinner_goal - (
                            breakfast_remaining + morning_remaining + lunch_remaining + afternoon_remaining + dinner_remaining))
            if current_hour < 22:
                # まだ夜時間内
                evening_remaining = max(0, evening_goal - evening_intake)
            else:
                # 夜時間を過ぎている場合は「達成済み」表示用に0にする
                evening_remaining = 0
        schedule.append({"時間帯": "夜 (20-22時)", "目標": evening_goal, "残り": evening_remaining})

        context.update({
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
        })

        return context

    def post(self, request, *args, **kwargs):
        # 現在の日付を取得
        today = timezone.localtime(timezone.now()).date()

        # 今日の記録を取得または作成
        intake, created = VitaminIntake.objects.get_or_create(
            user=self.request.user,
            date=today,
            defaults={'daily_goal': 10}
        )

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


class HistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'vitamin/history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 過去7日間の記録を取得（タイムゾーンを考慮）
        end_date = timezone.localtime(timezone.now()).date()
        start_date = end_date - timedelta(days=6)
        date_range = [start_date + timedelta(days=i) for i in range(7)]

        intakes = []
        for date in date_range:
            intake, created = VitaminIntake.objects.get_or_create(
                user=self.request.user,
                date=date,
                defaults={'daily_goal': 20}
            )
            intakes.append(intake)

        context.update({
            'intakes': intakes,
            'today': end_date,
        })

        return context