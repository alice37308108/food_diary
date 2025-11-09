# Generated manually - Data migration

from django.db import migrations


def create_initial_vegetable_types(apps, schema_editor):
    VegetableType = apps.get_model('nukazuke', 'VegetableType')
    
    # 既存の選択肢から野菜タイプを作成
    initial_vegetables = [
        ('cucumber', 'きゅうり', '🥒'),
        ('eggplant', 'なす', '🍆'),
        ('carrot', 'にんじん', '🥕'),
        ('cabbage', 'キャベツ', '🥬'),
        ('pepper', 'ピーマン', '🌶️'),
        ('tomato', 'トマト', '🍅'),
        ('radish', 'だいこん', '🌶️'),
        ('turnip', 'かぶ', '🌰'),
        ('other', 'その他', '🥗'),
    ]
    
    for old_key, name, emoji in initial_vegetables:
        VegetableType.objects.get_or_create(
            name=name,
            defaults={'emoji': emoji}
        )


def reverse_create_initial_vegetable_types(apps, schema_editor):
    VegetableType = apps.get_model('nukazuke', 'VegetableType')
    VegetableType.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('nukazuke', '0002_vegetabletype'),
    ]

    operations = [
        migrations.RunPython(
            create_initial_vegetable_types,
            reverse_create_initial_vegetable_types,
        ),
    ]
