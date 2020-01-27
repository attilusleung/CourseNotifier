#!/usr/bin/env python3
from argparse import ArgumentParser
from configparser import ConfigParser

import json
from io import StringIO
import os
import sys
from time import sleep
from twilio.rest import Client

from adddrop.query import find_all_openings
from adddrop.logger import get_logger

# TODO: ABS PATH
CONFIG_PATH = 'config.ini'
SECRETS_PATH = 'secrets/secrets.ini'
LOG_NAME = "main.log"
DEPENDENCIES_PATH = ['adddrop/query.py', 'adddrop/logger.py']

# TODO: logs
logger = get_logger(__name__, LOG_NAME)

argparser = ArgumentParser(
    description='Checks availability of Cornell classes')
# argparser.add_argument(
#   '--classes', nargs='+',
#   default=None, help='Read from list of class codes')
argparser.add_argument('--sem', default="", help='Use semester code provided')
args = argparser.parse_args()

sem = args.sem
classes = {}

confparser = ConfigParser()
confparser.optionxform = lambda option: option

if not classes or not sem:
    assert confparser.read(CONFIG_PATH), "Failed to read config file"

    if not classes:

        def parse_config(section):
            ret = {}
            for k, v in confparser[section].items():
                # print(v)
                ret[k] = json.loads(v)
            return ret

        sections = confparser.sections()
        try:
            sections.remove('SETTINGS')
        except ValueError:
            pass
        for s in sections:
            classes[s] = parse_config(s)

    sem = sem or confparser['SETTINGS']['Semester']

logger.info('Watching classes %s from %s', str(classes.keys()), sem)

WATCHED_FILES = [CONFIG_PATH, SECRETS_PATH, __file__, *DEPENDENCIES_PATH]
WATCHED_FILES_MTIMES = [(f, os.path.getmtime(f)) for f in WATCHED_FILES]


def check_mtimes():
    for f, m in WATCHED_FILES_MTIMES:
        if os.path.getmtime(f) != m:
            logger.warning('Watched files changed, restarting script')
            os.execv(__file__, sys.argv)


assert SECRETS_PATH in confparser.read(SECRETS_PATH)
secrets = confparser['TWILIO']
message_client = Client(secrets['SID'], secrets['AUTH'])
msg_builder = ConfigParser()
msg_builder.optionxform = lambda option: option


def intersect_class_dicts(openings, class_dict):
    return dict([(x, [y for y in openings[x] if y.number in class_dict[x]])
                 for x in openings.keys() if x in class_dict])


def minus_dicts(dict1, dict2):
    return dict([(x, [y for y in dict1[x]
                      if y not in dict2[x]]) if x in dict2 else (x, dict1[x])
                 for x in dict1.keys()])


def str_dict_items(d):
    return dict([(k, "\n" + "\n".join([str(i) for i in v]))
                 for k, v in d.items()])


def str_all(d):
    return dict([(k, str_dict_items(v)) for k, v in d.items()])


prev = {}
while (True):
    try:
        openings = find_all_openings(classes.keys(), sem)
        # print(openings)

        classes_open = dict([(c, intersect_class_dicts(s, classes[c]))
                             for c, s in openings.items() if c in classes])
        # print(classes_open)

        # if any([all([s for s in c.values()])
        #         for c in classes_open.values() if c]):
        #     logger.info('there are openings in at least 1 class!')

        if classes_open != prev:
            logger.info('Class status changed')
            msg_builder.clear()
            msg_builder.read_dict(str_all(classes_open))
            sio = StringIO()
            msg_builder.write(sio)

            changes = dict([(c, minus_dicts(s, prev[c])) if c in prev else
                            (c, s) for c, s in classes_open.items()])
            msg_builder.clear()
            msg_builder.read_dict(str_all(changes))
            ssio = StringIO()
            msg_builder.write(ssio)

            logger.info(sio.getvalue())
            message = message_client.messages.create(
                body=(f"Change in tracked classes "
                      f"\n\nChanges: \n{ssio.getvalue()} "
                      f"\n\nAll Open Classes: \n{sio.getvalue()}"),
                from_=confparser['TWILIO']['SOURCE_PHONE'],
                to=confparser['TWILIO']['DEST_PHONE'])
            logger.info("Set message @ %s", message.sid)
            prev = classes_open
        sleep(5)
        check_mtimes()
    except Exception:
        logger.exception('Unhandled exception during main loop')
        from traceback import format_exc
        message = message_client.messages.create(
            body=f"Unhandled exception during main loop \n\n{format_exc()}",
            from_=confparser['TWILIO']['SOURCE_PHONE'],
            to=confparser['TWILIO']['DEST_PHONE'])
        logger.error('Stacktrace sent as sms')
        raise
