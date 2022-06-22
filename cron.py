"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2022 RedFantom

If you make any improvements, please share them!
"""
import caldav
from datetime import datetime, timedelta
import ics
from collections import namedtuple
import uuid
from urllib.parse import quote
import sys
import re
import requests
import yaml


def printf(*args, **kwargs):
    kwargs.update({"end": "", "flush": True})
    print(*args, **kwargs)


with open(sys.argv[-1], "r") as fi:
    config = yaml.load(fi, yaml.CLoader)

HOST = config["calendar"]["url"]
USERNAME = config["calendar"]["username"]
PASSWORD = config["calendar"]["password"]
TARGET = config["calendar"]["name"]

ICAL_SOURCES = config["sources"]
RANGE_MIN, RANGE_MAX = config["range"]["min"], config["range"]["max"]

printf("Connecting to calendar host... ")
client = caldav.DAVClient(url=HOST, username=USERNAME, password=PASSWORD)
principal = client.principal()

if TARGET not in [calendar.name for calendar in principal.calendars()]:
    target: caldav.Calendar = principal.make_calendar(TARGET)
else:
    target: caldav.Calendar = principal.calendar(TARGET)
printf("Done.\n")

printf("Deleting existing events...")
for event in target.events():  # type: caldav.Event
    printf(".")
    event.delete()
printf("Done.\n")

url = namedtuple("Url", ["path"])


def _create(self, data, id=None, path=None):
    """Override for the caldav create function to fix a bug with the path-finding"""
    if path is None:
        path = HOST
    if id is None and path is not None and str(path).endswith('.ics'):
        id = re.search('(/|^)([^/]*).ics', str(path)).group(2)
    elif id is None:
        for obj_type in ('vevent', 'vtodo', 'vjournal', 'vfreebusy'):
            obj = None
            if hasattr(self.vobject_instance, obj_type):
                obj = getattr(self.vobject_instance, obj_type)
            elif self.vobject_instance.name.lower() == obj_type:
                obj = self.vobject_instance
            if obj is not None:
                try:
                    id = obj.uid.value
                except AttributeError:
                    id = str(uuid.uuid1())
                    obj.add('uid')
                    obj.uid.value = id
                break
    else:
        for obj_type in ('vevent', 'vtodo', 'vjournal', 'vfreebusy'):
            obj = None
            if hasattr(self.vobject_instance, obj_type):
                obj = getattr(self.vobject_instance, obj_type)
            elif self.vobject_instance.name.lower() == obj_type:
                obj = self.vobject_instance
            if obj is not None:
                if not hasattr(obj, 'uid'):
                    obj.add('uid')
                obj.uid.value = id
                break
    path += "/" + TARGET.lower() + "/" + quote(id.replace('/', '%2F')) + ".ics"
    path = self.parent.url.join(path)
    r = self.client.put(path, data, {"Content-Type": 'text/calendar; charset="utf-8"'})
    if not (r.status in (204, 201)):
        raise Exception(r)
    self.id = id


caldav.CalendarObjectResource._create = _create

for i, source in enumerate(ICAL_SOURCES):
    printf("Syncing Calendar {}...".format(i))
    ical = ics.Calendar(requests.get(source).text)
    for event in ical.events:  # type: ics.Event
        # TODO: This is a filter used by the author, not mandatory
        if event.all_day:
            continue
        target.save_event(
            # TODO: Improve this code when icalevents and caldav start playing nice with one another
            dtstart=event.begin.datetime if not event.all_day else event.begin.datetime.date(),
            dtend=event.end.datetime if not event.all_day else None,
            summary=event.description if event.description in ("Free", "Busy", "Away", "Tentative", "Working elsewhere") else "Busy",
        )
        printf(".")
    printf("Done.\n")
