# -*- encoding: utf-8 -*- 

import feedparser
import pprint
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import logging
import re

logger = logging.getLogger(__name__)

def get_tomorrow(*args, **kwargs):
    return get_date((datetime.today() + timedelta(days=1)).date(), *args, **kwargs)

def get_today(*args, **kwargs):
    return get_date(datetime.today().date(), *args, **kwargs)

# wod= could also be "Competition" - comparison is case insensitive btw
def get_date(date, wod="WOD"):

    url = "http://www.crossfit-rhein-neckar.de/category/wod/feed/"

    d = feedparser.parse(url)

    for article in d["entries"]:
        title = article["title"].strip()

        if wod.lower() not in title.lower():
            continue
        print title
        wod_date_pattern = re.compile(ur'^(\s?\w+\s?)?(?P<wod_date>\d{6}).*')
        match = wod_date_pattern.match(title)
        if not match:
            logger.debug("Pattern not found in title '%s'", title)
            continue

        wod_date = match.group('wod_date')
        print wod_date
        wod_date = datetime.strptime(wod_date, "%y%m%d")

        if wod_date.date() != date:
            continue

        published_date =  article["published_parsed"]
        soup = BeautifulSoup(article["content"][0]["value"], "html.parser")
        fb_div =  soup.find("div", class_="wpfblike")
        for superfluous in fb_div.find_next_siblings():
            superfluous.decompose()
        fb_div.decompose()
        for br in soup.find_all("br"):
            br.replace_with("\n")
        text = ""
        for string in soup.strings:
            text += string
        return (title, wod_date, text)

    

if __name__ == '__main__':
    pprint.pprint(get_today())
    pprint.pprint(get_tomorrow(wod="Competition"))

