from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime, timedelta
from .models import DailyCheck
import json


def index(request):
    # 食材カテゴリの定義
    food_categories = [
        {'key': 'ま', 'name': '豆類', 'examples': '大豆、納豆、豆腐、味噌など'},
        {'key': 'ご', 'name': 'ごま', 'examples': 'ごま、ナッツ類など'},
        {'key': 'は', 'name': 'わかめ', 'examples': 'わかめ、のり、ひじきなど'},
        {'key': 'や', 'name': 'やさい', 'examples': '野菜全般'},
        {'key': 'さ', 'name': 'さかな', 'examples': '魚、魚介類'},
        {'key': 'し', 'name': 'しいたけ', 'examples': 'しいたけ、きのこ類'},
        {'key': 'い', 'name': 'いも類', 'examples': 'さつまいも、じゃがいもなど'},
        {'key': '生', 'name': '生野菜', 'examples': 'サラダなど'},
        {'key': '発酵', 'name': '発酵食品', 'examples': '納豆、キムチ、ヨーグルトなど'},
    ]

    # 食事時間帯の定義
    meal_times = ['あさ', 'ひる', 'よる']

    # セッションから日付を取得（なければ今日）
    current_date_str = request.session.get('current_date', timezone.now().strftime('%Y-%m-%d'))
    current_date = datetime.strptime(current_date_str, '%Y-%m-%d').date()

    # POSTリクエスト処理
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'prev_day':
            # 前日に移動
            current_date = current_date - timedelta(days=1)
            request.session['current_date'] = current_date.strftime('%Y-%m-%d')
            return redirect('gut_health:index')

        elif action == 'next_day':
            # 翌日に移動
            current_date = current_date + timedelta(days=1)
            request.session['current_date'] = current_date.strftime('%Y-%m-%d')
            return redirect('gut_health:index')

        elif action == 'today':
            # 今日に移動
            current_date = timezone.now().date()
            request.session['current_date'] = current_date.strftime('%Y-%m-%d')
            return redirect('gut_health:index')

        elif action == 'toggle_check':
            # チェック切り替え
            category = request.POST.get('category')
            meal = request.POST.get('meal')

            # 該当日のデータを取得または作成
            daily_check, created = DailyCheck.objects.get_or_create(
                date=current_date,
                defaults={'data': json.dumps({})}
            )

            # 現在のデータを取得
            data = json.loads(daily_check.data)

            # 該当する食事時間帯がなければ初期化
            if meal not in data:
                data[meal] = {}

            # チェック状態を切り替え
            data[meal][category] = not data[meal].get(category, False)

            # データを保存
            daily_check.data = json.dumps(data)
            daily_check.save()

            return redirect('gut_health:index')

        elif action == 'save_mood_memo':
            # 気分とメモを保存
            mood = request.POST.get('mood')
            memo = request.POST.get('memo', '')

            # 該当日のデータを取得または作成
            daily_check, created = DailyCheck.objects.get_or_create(
                date=current_date,
                defaults={'data': json.dumps({})}
            )

            # 気分とメモを更新
            daily_check.mood = int(mood) if mood else None
            daily_check.memo = memo
            daily_check.save()

            return redirect('gut_health:index')

    # 該当日のデータを取得
    try:
        daily_check = DailyCheck.objects.get(date=current_date)
        data = json.loads(daily_check.data)
        mood = daily_check.mood
        memo = daily_check.memo
    except DailyCheck.DoesNotExist:
        # データがなければ空の辞書
        data = {}
        mood = None
        memo = ""

    # チェック状態を構築
    checks = {}
    for meal in meal_times:
        checks[meal] = {}
        for category in food_categories:
            if meal in data and category['key'] in data[meal]:
                checks[meal][category['key']] = data[meal][category['key']]
            else:
                checks[meal][category['key']] = False

    # 達成状況を計算（いずれかの食事で摂取していれば達成）
    achievement_status = {}
    for category in food_categories:
        achievement_status[category['key']] = any(
            meal_data.get(category['key'], False) for meal_data in data.values()
        )

    context = {
        'today': current_date,
        'food_categories': food_categories,
        'meal_times': meal_times,
        'checks': checks,
        'achievement_status': achievement_status,
        'mood': str(mood) if mood else None,
        'memo': memo,
    }

    return render(request, 'gut_health/index.html', context)


def history(request):
    # 履歴ページ
    from django.core.paginator import Paginator
    import json

    # フィルタリング条件の取得
    mood_filter = request.GET.get('mood', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    # クエリの構築
    checks_query = DailyCheck.objects.all().order_by('-date')

    # 調子フィルター
    if mood_filter and mood_filter.isdigit():
        checks_query = checks_query.filter(mood=int(mood_filter))

    # 日付範囲フィルター
    from datetime import datetime, timedelta

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            checks_query = checks_query.filter(date__gte=start_date)
        except ValueError:
            start_date = datetime.now().date() - timedelta(days=30)  # デフォルトは過去30日
    else:
        start_date = datetime.now().date() - timedelta(days=30)

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            checks_query = checks_query.filter(date__lte=end_date)
        except ValueError:
            end_date = datetime.now().date()
    else:
        end_date = datetime.now().date()

    # 食材カテゴリ定義
    food_categories = [
        {'key': 'ま', 'name': '豆類'},
        {'key': 'ご', 'name': 'ごま'},
        {'key': 'は', 'name': 'わかめ'},
        {'key': 'や', 'name': 'やさい'},
        {'key': 'さ', 'name': 'さかな'},
        {'key': 'し', 'name': 'しいたけ'},
        {'key': 'い', 'name': 'いも類'},
        {'key': '生', 'name': '生野菜'},
        {'key': '発酵', 'name': '発酵食品'},
    ]

    # 達成した食材カテゴリをリスト化
    checks_with_achievements = []
    for check in checks_query:
        data = json.loads(check.data)
        achievements = []
        achievement_count = 0

        for category in food_categories:
            # いずれかの食事で摂取していれば達成
            if any(meal_data.get(category['key'], False) for meal_data in data.values()):
                achievements.append(f"{category['key']}：{category['name']}")
                achievement_count += 1

        checks_with_achievements.append({
            'date': check.date,
            'mood': check.mood,
            'memo': check.memo,
            'achievements': achievements,
            'achievement_count': achievement_count
        })

    # ページネーション
    paginator = Paginator(checks_with_achievements, 10)  # 1ページあたり10件
    page = request.GET.get('page', 1)
    checks = paginator.get_page(page)

    context = {
        'checks': checks,
        'mood_filter': mood_filter,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'gut_health/history.html', context)