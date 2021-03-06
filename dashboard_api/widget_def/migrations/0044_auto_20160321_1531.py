# -*- coding: utf-8 -*-
#
#   Copyright 2016 NICTA
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from __future__ import unicode_literals

from django.db import migrations, models

from dashboard_api.migration_utils import *

def migrate_declaration(wd, apps):
    ViewWidgetDeclaration=apps.get_model("widget_def", "ViewWidgetDeclaration")
    view = migrate_view(apps, wd.theme, wd.frequency, wd.location)
    try:
        vwd=ViewWidgetDeclaration.objects.get(view=view, definition=wd.definition)
    except ViewWidgetDeclaration.DoesNotExist:
        vwd=ViewWidgetDeclaration(definition=wd.definition,
                                view=view,
                                sort_order=get_sort_order(ViewWidgetDeclaration, view=view))
        vwd.save()

def migrate_declarations(apps, schema_editor):
    WidgetDeclaration=apps.get_model("widget_def", "WidgetDeclaration")
    for wd in WidgetDeclaration.objects.all():
        migrate_declaration(wd, apps)

class Migration(migrations.Migration):

    dependencies = [
        ('widget_def', '0043_auto_20160321_1531'),
    ]

    operations = [
        migrations.RunPython(migrate_declarations),
    ]
