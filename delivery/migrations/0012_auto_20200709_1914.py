# Generated by Django 3.0.7 on 2020-07-09 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0011_auto_20200709_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='emoji',
            field=models.CharField(max_length=5),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='emoji',
            field=models.CharField(max_length=5),
        ),
    ]
