# Generated by Django 3.2.7 on 2021-12-24 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_auto_20211027_1534'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='thumbnail',
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('processing', 'processing'), ('shipped', 'shipped'), ('delivered', 'delivered')], default='processing', max_length=40),
        ),
    ]
