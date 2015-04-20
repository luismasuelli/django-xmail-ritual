# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AsyncEmailEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now, help_text='Message creation date (i.e. when send_mail was called on it)', verbose_name='Created')),
                ('tried_on', models.DateTimeField(default=None, help_text='Last try date', null=True, verbose_name='Tried')),
                ('content', models.TextField(help_text='Pickled message being sent (it is a pickled EmailMessage instance encoded in base 64)', verbose_name='Pickled e-mail')),
                ('state', models.CharField(default=b'pending', help_text='Current state of the message (pending, busy, already sent, or failed)', max_length=10, verbose_name='Message state', choices=[(b'pending', 'Pending'), (b'busy', 'Busy'), (b'failed', 'Failed'), (b'succeeded', 'Succeeded')])),
                ('last_error', models.TextField(help_text='Details for the last error occurred with this message', verbose_name='Last error', null=True, editable=False)),
                ('to', models.TextField(help_text='Prefetched destinations from the "to" field in the original message', verbose_name='To')),
                ('cc', models.TextField(help_text='Prefetched destinations from the "cc" field in the original message', null=True, verbose_name='Cc')),
                ('bcc', models.TextField(help_text='Prefetched destinations from the "bcc" field in the original message', null=True, verbose_name='Bcc')),
                ('subject', models.TextField(help_text='Prefetched subject from the original message', null=True, verbose_name='Subject')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
