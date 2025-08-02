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
    
    context = {
        'categories': categories,
        'recent_executions': recent_executions,
    }
    return render(request, 'comfort_list/index.html', context)

@login_required
def action_list(request):
    """全アクション一覧"""
    actions = ComfortAction.objects.filter(user=request.user).order_by('category', '-is_favorite', 'name')
    
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
        category=category
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
            messages.success(request, f'アクション「{action.name}」を追加しました！')
            return redirect('comfort_list:category_actions', category_name=action.category.name)
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
            return redirect('comfort_list:category_actions', category_name=action.category.name)
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
