import requests
from bs4 import BeautifulSoup
from collections import namedtuple
import os

from .logger import get_logger

BASE_LINK = "https://classes.cornell.edu/browse/roster"
SEMESTER = "FA19"
COURSE = "CS 3410"

LOG_NAME = "query.log"
logger = get_logger(__name__, LOG_NAME)

Section = namedtuple('Section', ['nbr', 'number', 'time'])
Section.__str__ = lambda self: f"[{self.number}]{self.nbr}: {self.time}"


def find_openings(course, semester=SEMESTER):
    link = "/".join([BASE_LINK, semester, "class", course.replace(' ', '/')])
    r = requests.get(link)
    page = BeautifulSoup(r.text, features="html.parser")

    assert page.find_all("h1", {"class": "sr-only"}), \
        ("Something went wrong. We accessed a "
         "different course than the one specified.")

    section = page.find_all("ul", {"class": "section"})
    openings = {}
    for s in section:
        if s.find("li", {"class": "open-status"}).\
                find("span", {"class": "tooltip-iws"})['data-content'] != "Open":
            continue
        component = s.find("em", {"title": "Component"}).string
        nbr = s.find("strong", {"title": "Class Number"}).string
        number = s['aria-label'].replace('Class Section',
                                         '').replace(component, '').strip()
        datetime = s.find("span", {"class": "pattern"})
        time = f'{datetime.find("span", {"class":"tooltip-iws"}).string} {datetime.find("time").string}'
        if component not in openings.keys():
            openings[component] = [Section(nbr=nbr, number=number, time=time)]
        else:
            openings[component].append(
                Section(nbr=nbr, number=number, time=time))

    return openings


def find_all_openings(courses, semester=SEMESTER):
    courses = set(courses)
    openings = {}
    for c in courses:
        try:
            openings[c] = find_openings(c, semester)
        except Exception:
            logger.exception('Skpping unparsable course %s.', c)
    return openings
