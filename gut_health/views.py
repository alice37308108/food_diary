import csv
import json
import urllib.parse
from datetime import datetime, timedelta

from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import View

from .models import DailyCheck


class IndexView(View):
    template_name = 'gut_health/index.html'

    def get_food_categories(self):
        """食材カテゴリの定義を返す"""
        return [
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

    def get_meal_times(self):
        """食事時間帯の定義を返す"""
        return ['あさ', 'ひる', 'よる']

    def get_current_date(self, request):
        """日付を取得する - タイムゾーン考慮版"""
        # URLパラメータでdateが指定されている場合はそれを使用
        date_param = request.GET.get('date')
        if date_param:
            try:
                return datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                pass

        # 常に今日の日付を表示する設定がセッションにある場合
        show_today = request.session.get('show_today', False)
        if show_today:
            return timezone.localtime(timezone.now()).date()

        # セッションに保存された日付があればそれを使用
        current_date_str = request.session.get('current_date')
        if current_date_str:
            try:
                return datetime.strptime(current_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        # それ以外は現在の日付を返す（ローカルタイムゾーン考慮）
        return timezone.localtime(timezone.now()).date()

    def get(self, request, *args, **kwargs):
        """GETリクエスト処理"""
        # 初回起動時には常に今日の日付を表示するフラグをセット
        if 'show_today' not in request.session:
            request.session['show_today'] = True

        food_categories = self.get_food_categories()
        meal_times = self.get_meal_times()
        current_date = self.get_current_date(request)

        # セッションに現在の日付を保存
        request.session['current_date'] = current_date.strftime('%Y-%m-%d')

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

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """POSTリクエスト処理"""
        action = request.POST.get('action')
        current_date = self.get_current_date(request)

        if action == 'prev_day':
            # 前日に移動
            current_date = current_date - timedelta(days=1)
            request.session['current_date'] = current_date.strftime('%Y-%m-%d')
            # 常に今日の日付を表示するフラグをオフ
            request.session['show_today'] = False
            return redirect('gut_health:index')

        elif action == 'next_day':
            # 翌日に移動
            current_date = current_date + timedelta(days=1)
            request.session['current_date'] = current_date.strftime('%Y-%m-%d')
            # 常に今日の日付を表示するフラグをオフ
            request.session['show_today'] = False
            return redirect('gut_health:index')

        elif action == 'today':
            # 今日に移動（ローカルタイムゾーン考慮）
            current_date = timezone.localtime(timezone.now()).date()
            request.session['current_date'] = current_date.strftime('%Y-%m-%d')
            # 常に今日の日付を表示するフラグをセット
            request.session['show_today'] = True
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

        # デフォルトはGETビューに渡す
        return self.get(request, *args, **kwargs)


class HistoryView(View):
    template_name = 'gut_health/history.html'

    def get_food_categories(self):
        """食材カテゴリの定義を返す"""
        return [
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

    def get(self, request, *args, **kwargs):
        """GETリクエスト処理"""
        # フィルタリング条件の取得
        mood_filter = request.GET.get('mood', '')
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')

        # クエリの構築
        checks_query = DailyCheck.objects.all().order_by('-date')

        # 調子フィルター
        if mood_filter and mood_filter.isdigit():
            checks_query = checks_query.filter(mood=int(mood_filter))

        # 日付範囲フィルター - タイムゾーン考慮
        today = timezone.localtime(timezone.now()).date()

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                checks_query = checks_query.filter(date__gte=start_date)
            except ValueError:
                start_date = today - timedelta(days=30)  # デフォルトは過去30日
        else:
            start_date = today - timedelta(days=30)

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                checks_query = checks_query.filter(date__lte=end_date)
            except ValueError:
                end_date = today
        else:
            end_date = today

        # 食材カテゴリ定義
        food_categories = self.get_food_categories()

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

        return render(request, self.template_name, context)


class ExportCSVView(View):
    """CSVエクスポート機能を提供するビュー"""

    def get_food_categories(self):
        """食材カテゴリの定義を返す"""
        return [
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

    def get_meal_times(self):
        """食事時間帯の定義を返す"""
        return ['あさ', 'ひる', 'よる']

    def get(self, request, *args, **kwargs):
        """CSVファイルを生成してダウンロードさせる"""
        # フィルターパラメータを取得
        mood_filter = request.GET.get('mood', '')
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')

        # クエリの構築
        checks_query = DailyCheck.objects.all().order_by('-date')

        # 調子フィルター
        if mood_filter and mood_filter.isdigit():
            checks_query = checks_query.filter(mood=int(mood_filter))

        # 日付範囲フィルター - タイムゾーン考慮
        today = timezone.localtime(timezone.now()).date()

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                checks_query = checks_query.filter(date__gte=start_date)
            except ValueError:
                start_date = today - timedelta(days=30)
        else:
            start_date = today - timedelta(days=30)

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                checks_query = checks_query.filter(date__lte=end_date)
            except ValueError:
                end_date = today
        else:
            end_date = today

        # 食材カテゴリ定義
        food_categories = self.get_food_categories()

        # 食事時間帯の定義
        meal_times = self.get_meal_times()

        # CSVファイルの作成 - BOMつきUTF-8で文字化け対策
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        filename = f"腸活チェック_{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}.csv"
        # ファイル名を日本語対応するためにURLエンコード
        quoted_filename = urllib.parse.quote(filename)
        response[
            'Content-Disposition'] = f'attachment; filename="{quoted_filename}"; filename*=UTF-8\'\'{quoted_filename}'

        # CSVライターの作成
        writer = csv.writer(response)

        # ヘッダー行の作成
        header = ['日付', '調子', '達成数', '摂取した食材', 'メモ']

        # 詳細情報のカラム追加
        for category in food_categories:
            for meal in meal_times:
                header.append(f"{category['key']}({meal})")

        writer.writerow(header)

        # データ処理
        for check in checks_query:
            data = json.loads(check.data)
            achievements = []
            achievement_count = 0

            # 各カテゴリの達成状況を計算
            for category in food_categories:
                # いずれかの食事で摂取していれば達成
                if any(meal_data.get(category['key'], False) for meal_data in data.values()):
                    achievements.append(f"{category['key']}：{category['name']}")
                    achievement_count += 1

            # 基本情報の行を作成
            row = [
                check.date.strftime('%Y/%m/%d'),  # 日付
                check.mood if check.mood else '',  # 調子
                achievement_count,  # 達成数
                ' '.join(achievements),  # 摂取した食材（スペース区切り）
                check.memo,  # メモ
            ]

            # 詳細情報（カテゴリ×食事時間の組み合わせ）
            for category in food_categories:
                for meal in meal_times:
                    # 該当の食事時間と食材カテゴリのチェック状態
                    checked = False
                    if meal in data and category['key'] in data[meal]:
                        checked = data[meal][category['key']]
                    row.append('○' if checked else '')  # チェックがある場合は「○」、ない場合は空欄

            writer.writerow(row)

        return response


class ExportCSVFormView(View):
    """CSVエクスポート設定フォームを表示するビュー"""

    template_name = 'gut_health/export_csv.html'

    def get(self, request, *args, **kwargs):
        """GETリクエスト処理"""
        # 現在の日付を取得（タイムゾーン考慮）
        today = timezone.localtime(timezone.now()).date()

        # デフォルトの日付範囲（過去30日）
        start_date = today - timedelta(days=30)
        end_date = today

        # リクエストから日付範囲を取得（あれば）
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')
        mood_filter = request.GET.get('mood', '')

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        context = {
            'start_date': start_date,
            'end_date': end_date,
            'mood_filter': mood_filter,
        }

        return render(request, self.template_name, context)