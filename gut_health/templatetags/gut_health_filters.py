from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """辞書から値を取得するためのテンプレートフィルター"""
    return dictionary.get(key, {})