#!/usr/bin/env python
# Kongregate stats parser.

# Copyright (c) 2008-2010 Corbin Simpson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from __future__ import division

import collections
import datetime
import json
import urllib2

class BadgeDict(dict):
    def __init__(self, iterable=[]):
        super(BadgeDict, self).__init__()

        for entry in iterable:
            self[entry["id"]] = entry

    def __getattr__(self, name):
        type, chaff, target = name.partition("_by_")
        if not target:
            raise AttributeError, "No target provided"

        if type == "count":
            def f(self):
                d = collections.defaultdict(int)
                for entry in self.itervalues():
                    d[entry[target]] += 1
                return d

            setattr(self.__class__, name, f)
        elif type == "iter":
            def f(self, filter):
                for entry in self.itervalues():
                    if entry[target] == filter:
                        yield entry
            setattr(self.__class__, name, f)
        else:
            raise AttributeError, "Unknown type %s" % type

        return getattr(self, name)

def acquire_json(name, d={}):
    if name not in d:
        print "Acquiring %s..." % name,
        handle = urllib2.urlopen("http://www.kongregate.com/%s.json" % name)
        data = handle.read()
        d[name] = json.loads(data)
        print "OK!"
    return d[name]

class Kongregate(object):
    def __init__(self):
        """
        Create an instance of the Kongregate API.

        Automatically retrieves information as needed from Kongregate.
        """

        badge_json = acquire_json("badges")
        self.badges = BadgeDict(badge_json)

class User(object):
    def __init__(self, kong, username):
        """
        Create an instance representing a Kongregate user.

        :Parameters:
            kong : `Kongregate`
                A Kongregate API handle.
            username : str
                The account username. Case-insensitive.
        """

        account_badges_json = acquire_json("accounts/%s/badges" % username)
        badge_keys = set(i["badge_id"] for i in account_badges_json)
        self.badges = BadgeDict()
        # Populate our BadgeDict with only the badges we've earned
        self.badges.update((key, value)
            for key, value in kong.badges.iteritems()
            if key in badge_keys)

def print_percentage(label, current, total):
    """
    Pretty-print a percentage in a uniform manner.
    """

    return "- %s: %d of %d (%2.2f%%)" % (label, current, total,
        (current * 100) / total)

def stats(account_name):
    """
    Print badge statistics.
    """

    kong = Kongregate()
    user = User(kong, account_name)

    retval = []

    account_json = acquire_json("accounts/%s" % account_name)

    start_date = account_json["created_at"]
    then = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    today = datetime.date.today()
    day_delta = today - then.date()

    retval.append("-- copy below this line --")
    retval.append(today.strftime("%B %d, %Y"))

    retval.append(print_percentage("Acquired Badges", len(user.badges),
            len(kong.badges)))

    difficulty_counts = kong.badges.count_by_difficulty()
    user_difficulty_counts = user.badges.count_by_difficulty()
    for difficulty in ("easy", "medium", "hard", "impossible"):
        retval.append(print_percentage("%ss" % difficulty.capitalize(),
                user_difficulty_counts[difficulty],
                difficulty_counts[difficulty]))

    total_points_from_badges = sum(badge["points"] for badge in
        user.badges.itervalues())

    retval.append(print_percentage("Points from Badges",
            total_points_from_badges, account_json["points"]))

    retval.append("- Average Points per Badge: %.2f" %
        (total_points_from_badges / len(user.badges)))

    badges_per_day = len(user.badges) / day_delta.days

    retval.append("- Average Badges per Day: %.2f" % badges_per_day)

    days_remaining = (len(kong.badges) - len(user.badges)) / badges_per_day

    retval.append("- Estimated date of completion: %s" %
        (today + datetime.timedelta(days_remaining)).strftime("%B %d, %Y"))

    retval.append("-- end of stats --")

    return retval
