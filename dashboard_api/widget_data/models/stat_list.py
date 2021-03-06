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

from decimal import Decimal, ROUND_HALF_UP
import datetime
import pytz

from django.conf import settings
from django.db import models

# Create your models here.
tz = pytz.timezone(settings.TIME_ZONE)

class StatisticListItem(models.Model):
    SECOND = 1
    MINUTE = 2
    HOUR = 3
    DAY = 4
    MONTH = 5
    QUARTER = 6
    YEAR = 7
    levels = [ "N/A", "second", "minute", "hour",
               "day", "month", "quarter", "year" ]
    level_choices = [
        ( SECOND, "second" ),
        ( MINUTE, "minute" ),
        ( HOUR, "hour" ),
        ( DAY, "day" ),
        ( MONTH, "month" ),
        ( QUARTER, "quarter" ),
        ( YEAR, "year" ),
    ]
    statistic = models.ForeignKey("widget_def.Statistic")
    param_value = models.ForeignKey("widget_def.ParametisationValue", null=True, blank=True)
    keyval = models.CharField(max_length=120, null=True, blank=True)
    datetime_key = models.DateTimeField(null=True, blank=True)
    datetime_keylevel = models.SmallIntegerField(choices=level_choices, 
                        null=True, blank=True)
    intval = models.IntegerField(blank=True, null=True)
    decval = models.DecimalField(max_digits=10, decimal_places=4,
                        blank=True, null=True)
    strval = models.CharField(max_length=400, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    traffic_light_code = models.ForeignKey("widget_def.TrafficLightScaleCode", blank=True, null=True)
    icon_code = models.ForeignKey("widget_def.IconCode", blank=True, null=True)
    trend = models.SmallIntegerField(choices=(
                    (1, "Upwards"),
                    (0, "Steady"),
                    (-1, "Downwards"),
                ), blank=True, null=True)
    sort_order = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    def display_val(self):
        if self.statistic.is_numeric():
            if self.statistic.num_precision == 0:
                return unicode(self.intval)
            else:
                return unicode(self.decval.quantize(Decimal(10)**(-1 * self.statistic.num_precision), ROUND_HALF_UP))
        else:
            return self.strval
    def set_datetime_key(self, key, level=None):
        if level is not None:
            level = int(level)
        if self.statistic.use_datekey():
            self.datetime_key = tz.localize(datetime.datetime.combine(key, datetime.time()))
        elif self.statistic.use_datetimekey():
            if level is None or level == self.SECOND:
                self.datetime_key = key
            elif level == self.MINUTE:
                key = key.replace(second=0)
                self.datetime_key = key
            elif level == self.HOUR:
                key = key.replace(second=0)
                key = key.replace(minute=0)
                self.datetime_key = key
            elif level == self.DAY:
                key = key.replace(second=0)
                key = key.replace(minute=0)
                key = key.replace(hour=0)
                self.datetime_key = key
            elif level == self.MONTH:
                key = key.replace(second=0)
                key = key.replace(minute=0)
                key = key.replace(hour=0)
                key = key.replace(day=1)
                self.datetime_key = key
            elif level == self.QUARTER:
                key = key.replace(second=0)
                key = key.replace(minute=0)
                key = key.replace(hour=0)
                key = key.replace(day=1)
                key = key.replace(month=((key.month - 1) / 3) * 3 + 1)
                self.datetime_key = key
            elif level == self.YEAR:
                key = key.replace(second=0)
                key = key.replace(minute=0)
                key = key.replace(hour=0)
                key = key.replace(day=1)
                key = key.replace(month=1)
                self.datetime_key = key
            else:
                raise Exception("set_datetime_key: Invalid level passed: %s" % repr(level))
            self.datetime_keylevel=level
        else:
            raise Exception("set_datetime_key called on non date(time) key statistic: %s" % repr(level))
    def display_datetime_key(self):
        if self.statistic.use_datekey():
            return self.datetime_key.strftime("%Y-%m-%d")
        elif self.statistic.use_datetimekey():
            if self.datetime_keylevel in (None, self.SECOND, self.MINUTE, self.HOUR):
                return self.datetime_key.astimezone(tz).strftime("%Y-%m-%dT%H:%M:%S")
            elif self.datetime_keylevel in (self.DAY, self.MONTH):
                return self.datetime_key.astimezone(tz).strftime("%Y-%m-%d")
            elif self.datetime_keylevel == self.QUARTER:
                qtr = (self.datetime_key.astimezone(tz).month - 1)/3 + 1
                return "%dQ%d" % (self.datetime_key.astimezone(tz).year, qtr)
            else: # self.datetime_keylevel == self.YEAR:
                return self.datetime_key.astimezone(tz).strftime("%Y")
        else:
            return None
    def value(self):
        if self.statistic.is_numeric():
            if self.statistic.num_precision == 0:
                return self.intval
            else:
                return self.decval.quantize(Decimal(10)**(-1 * self.statistic.num_precision), ROUND_HALF_UP)
        else:
            return self.strval
    def __unicode__(self):
        if self.param_value:
            return "<List for %s (%s) (%d)>" % (unicode(self.statistic), repr(self.param_value.parameters()), self.sort_order)
        else:
            return "<List for %s (%d)>" % (unicode(self.statistic), self.sort_order)
    class Meta:
        unique_together = ("statistic", "param_value", "datetime_key", "datetime_keylevel", "sort_order")
        ordering = ("param_value", "statistic", "datetime_key", "-datetime_keylevel", "sort_order")

