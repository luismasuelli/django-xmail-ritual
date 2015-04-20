# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xmail', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='asyncemailentry',
            options={'verbose_name': 'Async e-mail entry', 'verbose_name_plural': 'Async e-mail entries'},
        ),
    ]
