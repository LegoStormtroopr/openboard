# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-17 01:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0058_auto_20160617_1124'),
        ('widget_data', '0017_auto_20160610_1022'),
    ]

    operations = [
        migrations.CreateModel(
            name='GraphClusterData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(max_length=200)),
                ('cluster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='widget_def.GraphCluster')),
                ('param_value', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='widget_def.ParametisationValue')),
            ],
        ),
        migrations.CreateModel(
            name='GraphDatasetData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(max_length=200)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='widget_def.GraphDataset')),
                ('param_value', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='widget_def.ParametisationValue')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='graphdatasetdata',
            unique_together=set([('dataset', 'param_value')]),
        ),
        migrations.AlterUniqueTogether(
            name='graphclusterdata',
            unique_together=set([('cluster', 'param_value')]),
        ),
    ]
