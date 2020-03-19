# Generated by Django 2.2 on 2020-03-19 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xmail', '0002_auto_20150419_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asyncemailentry',
            name='state',
            field=models.CharField(choices=[('pending', 'Pending'), ('busy', 'Busy'), ('failed', 'Failed'), ('succeeded', 'Succeeded')], default='pending', help_text='Current state of the message (pending, busy, already sent, or failed)', max_length=10, verbose_name='Message state'),
        ),
    ]