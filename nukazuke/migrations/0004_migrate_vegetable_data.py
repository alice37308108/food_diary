# Generated manually - Data migration

from django.db import migrations


def migrate_vegetable_data(apps, schema_editor):
    PickledVegetable = apps.get_model('nukazuke', 'PickledVegetable')
    VegetableType = apps.get_model('nukazuke', 'VegetableType')
    
    # 既存の選択肢とVegetableTypeのマッピング
    mapping = {
        'cucumber': 'きゅうり',
        'eggplant': 'なす',
        'carrot': 'にんじん',
        'cabbage': 'キャベツ',
        'pepper': 'ピーマン',
        'tomato': 'トマト',
        'radish': 'だいこん',
        'turnip': 'かぶ',
        'other': 'その他',
    }
    
    # 新しいフィールドを追加（一時的）
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        schema_editor.execute(
            "ALTER TABLE nukazuke_pickledvegetable ADD COLUMN vegetable_type_new_id INTEGER"
        )
    
    # データを移行
    for pickled_vegetable in PickledVegetable.objects.all():
        old_type = pickled_vegetable.vegetable_type
        new_name = mapping.get(old_type, 'その他')
        
        try:
            vegetable_type = VegetableType.objects.get(name=new_name)
            # 直接SQLで更新
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE nukazuke_pickledvegetable SET vegetable_type_new_id = %s WHERE id = %s",
                    [vegetable_type.id, pickled_vegetable.id]
                )
        except VegetableType.DoesNotExist:
            # その他を使用
            other_type = VegetableType.objects.get(name='その他')
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE nukazuke_pickledvegetable SET vegetable_type_new_id = %s WHERE id = %s",
                    [other_type.id, pickled_vegetable.id]
                )


def reverse_migrate_vegetable_data(apps, schema_editor):
    # 逆操作は複雑なので、警告のみ
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('nukazuke', '0003_populate_vegetabletype'),
    ]

    operations = [
        migrations.RunPython(
            migrate_vegetable_data,
            reverse_migrate_vegetable_data,
        ),
    ]
