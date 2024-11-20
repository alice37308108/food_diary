# Generated by Django 4.2 on 2024-11-12 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gratitude', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, verbose_name='カテゴリー名')),
            ],
        ),
        migrations.AlterField(
            model_name='gratitudephrase',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gratitude.category', verbose_name='ジャンル'),
        ),
    ]