# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nukazuke', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VegetableType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='野菜名')),
                ('emoji', models.CharField(default='🥗', max_length=10, verbose_name='絵文字')),
                ('is_active', models.BooleanField(default=True, verbose_name='有効')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '野菜の種類',
                'verbose_name_plural': '野菜の種類',
                'ordering': ['name'],
            },
        ),
    ]
