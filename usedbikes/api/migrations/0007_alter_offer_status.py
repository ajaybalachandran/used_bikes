# Generated by Django 3.2.15 on 2022-10-04 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_sales_bike'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='status',
            field=models.CharField(choices=[('cancelled', 'cancelled'), ('approved', 'approved'), ('pending', 'pending'), ('sold-out', 'sold-out')], default='pending', max_length=120),
        ),
    ]
