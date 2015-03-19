# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0020_auto_20150319_1405'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='widgetdefinition',
            unique_together=set([('url', 'actual_frequency'), ('subcategory', 'sort_order')]),
        ),
        migrations.RemoveField(
            model_name='widgetdefinition',
            name='actual_frequency_url',
        ),
    ]
