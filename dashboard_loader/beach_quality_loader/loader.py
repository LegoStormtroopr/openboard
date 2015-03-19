import time
import datetime
import decimal
import re
import httplib
import xml.etree.ElementTree as ET

from dashboard_loader.loader_utils import LoaderException, set_statistic_data, clear_statistic_data,get_icon, get_statistic, clear_statistic_list, add_statistic_list_item, call_in_transaction

from beach_quality_loader.models import BeachSummaryHistory, CurrentBeachRating

# Refresh data every 3 hours
refresh_rate = 60*60*3

def update_data(loader, verbosity=0):
    messages = []
    http = httplib.HTTPConnection("www.environment.nsw.gov.au")
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/OceanBulletin.xml")
        resp = http.getresponse()
        messages.extend(call_in_transaction(process_xml,BeachSummaryHistory.SYDNEY_OCEAN, resp))
    except LoaderException, e:
        messages.append("Error updating Sydney Ocean beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/SydneyBulletin.xml")
        resp = http.getresponse()
        messages.extend(call_in_transaction(process_xml,BeachSummaryHistory.SYDNEY_HARBOUR, resp))
    except LoaderException, e:
        messages.append("Error updating Sydney Ocean beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/BotanyBulletin.xml")
        resp = http.getresponse()
        messages.extend(call_in_transaction(process_xml,BeachSummaryHistory.BOTANY_BAY, resp))
    except LoaderException, e:
        messages.append("Error updating Botany Bay beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/PittwaterBulletin.xml")
        resp = http.getresponse()
        messages.extend(call_in_transaction(process_xml,BeachSummaryHistory.PITTWATER, resp))
    except LoaderException, e:
        messages.append("Error updating Pittwater beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/CentralCoastBulletin.xml")
        resp = http.getresponse()
        messages.extend(call_in_transaction(process_xml,BeachSummaryHistory.CENTRAL_COAST, resp))
    except LoaderException, e:
        messages.append("Error updating Central Coast beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/IllawarraBulletin.xml")
        resp = http.getresponse()
        messages.extend(call_in_transaction(process_xml,BeachSummaryHistory.ILLAWARRA, resp))
    except LoaderException, e:
        messages.append("Error updating Illawarra beach data: %s" % unicode(e))
    try:
        http.request("GET", "http://www.environment.nsw.gov.au/beachapp/HunterBulletin.xml")
        resp = http.getresponse()
        messages.extend(call_in_transaction(process_xml,BeachSummaryHistory.HUNTER, resp))
    except LoaderException, e:
        messages.append("Error updating Hunter beach data: %s" % unicode(e))
    http.close()
    try:
        messages.extend(call_in_transaction(update_stats))
    except LoaderException, e:
        messages.append("Error updating widget stats: %s" % unicode(e))
    return messages

def update_stats():
    messages = []
    today = datetime.date.today()
    start_of_year = datetime.datetime(today.year, 1, 1)
    messages.extend(update_summary_stat(
            "beaches", "nsw", "day", "all_ocean_beaches",
            BeachSummaryHistory.objects.filter(
                region__in=BeachSummaryHistory.ocean_beaches,
                day=today),
            BeachSummaryHistory.objects.filter(
                region__in=BeachSummaryHistory.ocean_beaches,
                day=day_before(today))
            ))
    messages.extend(update_summary_stat(
            "beaches", "nsw", "day", "all_ocean_ytd",
            BeachSummaryHistory.objects.filter(
                region__in=BeachSummaryHistory.ocean_beaches,
                day__gte=start_of_year,
                day__lte=today
                )
            ))
    for region in BeachSummaryHistory.regions:
        messages.extend(update_summary_stat(
                "beaches", "nsw", "day", "region_%s" % region,
                BeachSummaryHistory.objects.filter(
                    region=region,
                    day=today
                    )
                ))
    messages.append("Statistics updated") 
    return messages

def day_before(d):
    dt = datetime.datetime.combine(d, datetime.time(0,0,0))
    dt -= datetime.timedelta(days=1)
    return dt.date

def update_summary_stat(widget_url, widget_location_url, widget_freq_url, statistic_url,
        beachsummary_set, trend_cmp_set=None):
    messages = []
    if not beachsummary_set:
        return ["Beach summary set for widget %s(%s,%s) is empty" % (widget_url, widget_location_url, widget_freq_url)]
    total_likely = 0
    total_possible = 0
    total_unlikely = 0
    for bs in beachsummary_set:
        total_likely += bs.num_pollution_likely
        total_possible += bs.num_pollution_possible
        total_unlikely += bs.num_pollution_unlikely
    (value, tlc) = summarise_quality(total_likely, total_possible, total_unlikely)
    if trend_cmp_set is None:
        trend = None
    elif trend_cmp_set:
        total_likely = 0
        total_possible = 0
        total_unlikely = 0
        for bs in trend_cmp_set:
            total_likely += bs.num_pollution_likely
            total_possible += bs.num_pollution_possible
            total_unlikely += bs.num_pollution_unlikely
        (trend_value, trend_tlc) = summarise_quality(total_likely, total_possible, total_unlikely)
        trend = value_cmp(trend_value, value) 
    else:
        messages.append("No past data to determine trend")
        trend = 0
    set_statistic_data(widget_url, widget_location_url, widget_freq_url, statistic_url, value,
                traffic_light_code = tlc, trend=trend)
    return messages

def value_cmp(old, new):
    if old == new:
        return 0
    elif old == "Poor":
        return 1
    elif old == "Good":
        return -1
    elif new == "Poor":
        return -1
    else:
        return 1

def summarise_quality(total_likely, total_possible, total_unlikely):
    total = float(total_likely + total_possible + total_unlikely)
    if total_likely/total > 0.2 or (total_possible + total_likely)/total > 0.7:
        return ("Poor", "bad")
    elif (total_possible + total_likely)/total > 0.4:
        return ("Fair", "poor")
    else:
        return ("Good", "good")

def process_xml(region, resp):
    xml = ET.parse(resp)
    title = BeachSummaryHistory.regions[region]
    # dump_xml(region, xml)
    num_unlikely = 0
    num_possible = 0
    num_likely = 0
    for elem in xml.getroot()[0]:
        if elem.tag == 'item':
            beach_name = None
            advice = None
            item = elem
            for i in item:
                if i.tag == 'title':
                    beach_name = i.text
                elif i.tag.endswith('}data'):
                    data = i
                    for d in data:
                        if d.tag.endswith('}advice'):
                            advice = d.text.strip()
            if not beach_name: 
                raise LoaderException("Parse error: Beach with no name")
            if not advice:
                raise LoaderException("Parse error: Beach %s has no advice" % beach_name)
            try:
                beach = CurrentBeachRating.objects.get(region=region, beach_name = beach_name)
            except CurrentBeachRating.DoesNotExist:
                beach = CurrentBeachRating(region=region, beach_name=beach_name)
            beach.rating = beach.parse_advice(advice)
            beach.save()
            if beach.rating == beach.GOOD:
                num_unlikely += 1
            elif beach.rating == beach.FAIR:
                num_possible += 1
            else:
                num_likely += 1
    try:
        summary = BeachSummaryHistory.objects.get(region=region, day=datetime.date.today())
    except BeachSummaryHistory.DoesNotExist:
        summary = BeachSummaryHistory(region=region)
    if num_unlikely + num_possible + num_likely == 0:
        raise LoaderException("No beaches found in RSS feed")
    summary.num_pollution_unlikely = num_unlikely
    summary.num_pollution_possible = num_possible
    summary.num_pollution_likely = num_likely
    summary.save()
    return ["Loaded data for %s beaches" % title]

def dump_xml(region, xml):
    title = BeachSummaryHistory.regions[region]
    print "%s:" % title
    for elem in xml.getroot()[0]:
        if elem.tag.endswith( '}data'):
            data = elem
            for d in data:
                if d.tag.endswith('}weather'):
                    print "Weather: %s" % d.text
                elif d.tag.endswith('}winds'):
                    print "Winds: %s" % d.text  
                elif d.tag.endswith('}rainfall'):
                    print "Rainfall: %s" % d.text  
                elif d.tag.endswith('}airTemp'):
                    print "Air Temp: %sdegC" % d.text  
                elif d.tag.endswith('}oceanTemp'):
                    print "Ocean Temp: %sdegC" % d.text  
                elif d.tag.endswith('}swell'):
                    print "Swell: %s" % d.text  
                elif d.tag.endswith('}highTide'):
                    print "High Tide: %s" % d.text  
                elif d.tag.endswith('}lowTide'):
                    print "Low Tide: %s" % d.text  
            print "-------------------------"
        elif elem.tag == 'item':
            item = elem
            for i in item:
                if i.tag == 'title':
                    print "Beach: %s" % i.text
                elif i.tag.endswith('}data'):
                    data = i
                    for d in data:
                        if d.tag.endswith('}advice'):
                            print "Advice: %s" % d.text.strip()
                        elif d.tag.endswith('}bsg'):
                            print "BSG: %s" % d.text  
                        elif d.tag.endswith('}starRating'):
                            print "Star Rating: %d" % len(d.text.strip())
                        elif d.tag.endswith('}latitude'):
                            print "lat: %s" % d.text  
                        elif d.tag.endswith('}longitude'):
                            print "long: %s" % d.text  
            print "-------------------------"
    print "======================================" 

