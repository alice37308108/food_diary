# Generated manually

from django.db import migrations, models
import django.db.models.deletion


def replace_vegetable_type_field(apps, schema_editor):
    from django.db import connection
    with connection.schema_editor() as schema_editor:
        # 古いフィールドを削除
        schema_editor.execute("ALTER TABLE nukazuke_pickledvegetable DROP COLUMN vegetable_type")
        # 新しいフィールドの名前を変更
        schema_editor.execute("ALTER TABLE nukazuke_pickledvegetable RENAME COLUMN vegetable_type_new_id TO vegetable_type_id")


def reverse_replace_vegetable_type_field(apps, schema_editor):
    # 逆操作は複雑なので実装しない
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('nukazuke', '0004_migrate_vegetable_data'),
    ]

    operations = [
        migrations.RunPython(
            replace_vegetable_type_field,
            reverse_replace_vegetable_type_field,
        ),
        # フィールドの定義を更新
        migrations.AlterField(
            model_name='pickledvegetable',
            name='vegetable_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nukazuke.vegetabletype', verbose_name='野菜の種類'),
        ),
    ]
