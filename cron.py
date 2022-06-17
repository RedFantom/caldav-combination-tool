"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2022 RedFantom

If you make any improvements, please share them!
"""
import caldav
from datetime import datetime, timedelta
# Yes, this library needs two import lines to allow importing of all necessary bits
# It is indeed missing an __init__.py file
from icalevents import icalevents as ical
from icalevents.icalparser import Event as ICalEvent
from collections import namedtuple
import uuid
from urllib.parse import quote
import re

# TODO: Set the information in this section
USERNAME = "Calendar"
PASSWORD = "PASSWORD"
HOST = "https://yourcloud.com/remote.php/dav/calendars/{}".format(USERNAME)
TARGET = "Personal"

ICAL_SOURCES = [
    # TODO: Add your ical sources here
]
RANGE = [timedelta(days=-30), timedelta(days=120)]

client = caldav.DAVClient(url=HOST, username=USERNAME, password=PASSWORD)
principal = client.principal()

if TARGET not in [calendar.name for calendar in principal.calendars()]:
    target: caldav.Calendar = principal.make_calendar(TARGET)
else:
    target: caldav.Calendar = principal.calendar(TARGET)

for event in target.events():  # type: caldav.Event
    event.delete()

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

for source in ICAL_SOURCES:
    events = ical.events(source, start=datetime.now() + RANGE[0], end=datetime.now() + RANGE[1])
    for event in events:  # type: ICalEvent
        # TODO: This is a filter used by the author, not mandatory
        if event.all_day:
            continue
        target.save_event(
            # TODO: Improve this code when icalevents and caldav start playing nice with one another
            dtstart=event.start if not event.all_day else event.start.date(),
            dtend=event.end if not event.all_day else None,
            summary=event.summary if event.summary in ("Free", "Busy", "Away", "Tentative", "Working elsewhere") else "Busy",
        )
