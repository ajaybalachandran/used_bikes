# Generated by Django 3.2.15 on 2022-09-28 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bikeimages',
            name='image',
            field=models.ImageField(default='Null', upload_to='bike-images'),
        ),
    ]
