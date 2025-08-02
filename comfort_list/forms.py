from django import forms
from .models import ComfortAction, ActionExecution, HappinessRecord, Category

class ComfortActionForm(forms.ModelForm):
    """心地よさアクション作成フォーム"""
    
    class Meta:
        model = ComfortAction
        fields = ['name', 'categories', 'description', 'estimated_minutes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例: 1分片付ける、深呼吸する'
            }),
            'categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '詳細な説明（任意）'
            }),
            'estimated_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 120,
                'placeholder': '所要時間（分）'
            }),
        }
        labels = {
            'name': 'アクション名',
            'categories': 'カテゴリ（複数選択可）',
            'description': '説明',
            'estimated_minutes': '所要時間（分）',
        }

class ActionExecutionForm(forms.ModelForm):
    """アクション実行記録フォーム"""
    
    class Meta:
        model = ActionExecution
        fields = ['comfort_level', 'memo']
        widgets = {
            'comfort_level': forms.Select(attrs={'class': 'form-control'}),
            'memo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '実行した感想やメモ（任意）'
            }),
        }
        labels = {
            'comfort_level': 'すっきり度',
            'memo': 'メモ',
        }

class HappinessRecordForm(forms.ModelForm):
    """小さな幸せ記録フォーム"""
    
    class Meta:
        model = HappinessRecord
        fields = ['title', 'content', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例: 美味しいコーヒーを飲んだ'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'どんな小さな幸せだったか詳しく書いてみましょう...'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'title': 'タイトル',
            'content': '内容',
            'photo': '写真（任意）',
        } 