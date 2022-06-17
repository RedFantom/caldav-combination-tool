# CalDAV Combination Tool
#### Combine multiple ical sources into a single CalDAV availability calendar!

This script is provided in the hope that it may be useful. It is used by
the author on a daily basis.

## What does it do?
Have you always wanted to have a single calendar you can share so that 
people know your availability, but not the details of your appointments?
Do you find that this is impossible because all tools you can find require
you to share all your different calendars (personal, work, sports, etc.)
separately with the people you want to share your availability with?

Now you can create a single CalDAV calendar that will contain all your
events, but not their details!

### How do I use it?
Simply setup a CalDAV server (I use Nextcloud), enter the information 
marked in the script (host, username, password, ical sources) and 
setup a CRON job to run the script. The CalDAV calendar will be read-only
from your end, the script will keep its contents up-to-date.

Make sure you do not use the CalDAV Calendar for anything else.

### How did you solve the 'source of truth' problem?
I didn't! The CalDAV Calendar is simply cleared before every update. Do
NOT edit the CalDAV calendar you set as a target.

### Can you implement feature _x_?
Probably not, as I have very little time to spend on programming right 
now. The `caldav` and `icalevents` libraries this script depends on are
also quite messy in their structure, so advanced features are difficult
to build.

**If you open a PR, I _will_ review it.** Maybe it will take me a week or
two, but PRs are always welcome.

### What is a cron-job?
This script is probably not intended for you if you do not (yet) know
what a cron-job is. But if you're set on it: [read here](https://en.wikipedia.org/wiki/Cron).