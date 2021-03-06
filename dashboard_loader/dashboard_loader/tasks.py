#   Copyright 2015 NICTA
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

from __future__ import absolute_import

from celery import shared_task

from dashboard_loader.loader_utils import do_update
from dashboard_loader.models import Loader

@shared_task
def update_app_data(app):
    return do_update(app)

@shared_task
def update_all_apps():
    updates_queued = 0
    loaders = Loader.objects.all()
    for loader in loaders:
        if not loader.reason_to_not_run():
            update_app_data.delay(loader.app)
            updates_queued += 1
    return updates_queued

