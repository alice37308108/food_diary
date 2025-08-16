from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Category, ComfortAction, ActionExecution, HappinessRecord
from .forms import ComfortActionForm, ActionExecutionForm, HappinessRecordForm

@login_required
def index(request):
    """心地よさリストのメインページ"""
    categories = Category.objects.all().order_by('id')
    recent_executions = ActionExecution.objects.filter(
        action__user=request.user
    ).order_by('-executed_at')[:5]
    
    # 重複なしの合計アクション数を取得
    total_actions_count = ComfortAction.objects.filter(user=request.user).count()
    
    # 各カテゴリのアクション数を計算（ユーザー別）
    categories_with_count = []
    for category in categories:
        actions_count = ComfortAction.objects.filter(
            user=request.user, 
            categories=category
        ).count()
        categories_with_count.append({
            'category': category,
            'actions_count': actions_count
        })
    
    context = {
        'categories_with_count': categories_with_count,
        'recent_executions': recent_executions,
        'total_actions_count': total_actions_count,
    }
    return render(request, 'comfort_list/index.html', context)

@login_required
def action_list(request):
    """全アクション一覧"""
    actions = ComfortAction.objects.filter(user=request.user).order_by('-is_favorite', 'name')
    
    context = {
        'actions': actions,
    }
    return render(request, 'comfort_list/action_list.html', context)

@login_required
def category_actions(request, category_name):
    """カテゴリ別アクション表示"""
    category = get_object_or_404(Category, name=category_name)
    actions = ComfortAction.objects.filter(
        user=request.user, 
        categories=category
    ).order_by('-is_favorite', 'name')
    
    context = {
        'category': category,
        'actions': actions,
    }
    return render(request, 'comfort_list/category_actions.html', context)

@login_required
def add_action(request):
    """アクション追加"""
    if request.method == 'POST':
        form = ComfortActionForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.user = request.user
            action.save()
            form.save_m2m()  # ManyToManyFieldを保存
            messages.success(request, f'アクション「{action.name}」を追加しました！')
            # 最初のカテゴリのページにリダイレクト
            first_category = action.categories.first()
            if first_category:
                return redirect('comfort_list:category_actions', category_name=first_category.name)
            else:
                return redirect('comfort_list:index')
    else:
        form = ComfortActionForm()
    
    context = {
        'form': form,
    }
    return render(request, 'comfort_list/add_action.html', context)

@login_required
def execute_action(request, action_id):
    """アクション実行記録"""
    action = get_object_or_404(ComfortAction, id=action_id, user=request.user)
    
    if request.method == 'POST':
        form = ActionExecutionForm(request.POST)
        if form.is_valid():
            execution = form.save(commit=False)
            execution.action = action
            execution.save()
            messages.success(request, f'「{action.name}」を実行しました！すっきり度: {execution.get_comfort_level_display()}')
            # 最初のカテゴリのページにリダイレクト
            first_category = action.categories.first()
            if first_category:
                return redirect('comfort_list:category_actions', category_name=first_category.name)
            else:
                return redirect('comfort_list:index')
    else:
        form = ActionExecutionForm()
    
    context = {
        'action': action,
        'form': form,
    }
    return render(request, 'comfort_list/execute_action.html', context)

@login_required
def happiness_list(request):
    """小さな幸せ一覧"""
    happiness_records = HappinessRecord.objects.filter(
        user=request.user
    ).order_by('-recorded_at')
    
    context = {
        'happiness_records': happiness_records,
    }
    return render(request, 'comfort_list/happiness_list.html', context)

@login_required
def add_happiness(request):
    """小さな幸せ追加"""
    if request.method == 'POST':
        form = HappinessRecordForm(request.POST, request.FILES)
        if form.is_valid():
            happiness = form.save(commit=False)
            happiness.user = request.user
            happiness.save()
            messages.success(request, f'小さな幸せ「{happiness.title}」を記録しました！')
            return redirect('comfort_list:happiness_list')
    else:
        form = HappinessRecordForm()
    
    context = {
        'form': form,
    }
    return render(request, 'comfort_list/add_happiness.html', context)

@login_required
def edit_action(request, action_id):
    """アクション編集"""
    action = get_object_or_404(ComfortAction, id=action_id, user=request.user)
    
    if request.method == 'POST':
        form = ComfortActionForm(request.POST, instance=action)
        if form.is_valid():
            form.save()
            messages.success(request, f'アクション「{action.name}」を更新しました！')
            # 最初のカテゴリのページにリダイレクト
            first_category = action.categories.first()
            if first_category:
                return redirect('comfort_list:category_actions', category_name=first_category.name)
            else:
                return redirect('comfort_list:index')
    else:
        form = ComfortActionForm(instance=action)
    
    context = {
        'form': form,
        'action': action,
    }
    return render(request, 'comfort_list/edit_action.html', context)

@login_required
def delete_action(request, action_id):
    """アクション削除"""
    action = get_object_or_404(ComfortAction, id=action_id, user=request.user)
    
    if request.method == 'POST':
        first_category = action.categories.first()
        action_name = action.name
        action.delete()
        messages.success(request, f'アクション「{action_name}」を削除しました。')
        if first_category:
            return redirect('comfort_list:category_actions', category_name=first_category.name)
        else:
            return redirect('comfort_list:index')
    
    context = {
        'action': action,
    }
    return render(request, 'comfort_list/delete_action.html', context)
