#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of DocOps, a documentation operations helper library.
# Copyright © 2016 seamus tuohy, <s2e@seamustuohy.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the included LICENSE file for details.

from urllib.request import urlopen
from urllib.error import HTTPError

import json

import logging
logging.basicConfig(level=logging.ERROR)
log = logging.getLogger(__name__)

def archive_url(target_url, submission_url="http://web.archive.org/save/"):
    """Submit a url to be archived
    """
    try:
        # Submit the url
        urlopen(submission_url + target_url)
    except HTTPError as e:
        response_info = e.info()
        archive_error = response_info['X-Archive-Wayback-Runtime-Error'].split(":")[0]
        if archive_error == "RobotAccessControlException":
            # 403 = Not allowing internet archive bot
            raise RobotAccessControlException("The url cannot be archived." +
                                              "Internet archives is blocked " +
                                              "from archiving it " +
                                              "by the sites robots.txt")
        elif archive_error == "LiveDocumentNotAvailableException":
            # 502 = Unavailable
            raise MissingArchiveError("The url could not be reached for " +
                                      "archiving. Check that the url " +
                                      "points to active site and try again.")

def get_archive_info(target_url, query_url="https://archive.org/wayback/available?url=", timestamp=None):
    """Get archive information for an archived item.

    Args:
        timestamp: The format of the timestamp is 1-14 digits (YYYYMMDDhhmmss)

    """
    archive_query = query_url + target_url
    if timestamp is None:
        archive_url = archive_query
    else:
        time_query = "&timestamp=" + timestamp
        archive_url = archive_query + time_query

    archive_check = urlopen(archive_url)
    # load json data
    archive_data = archive_check.read().decode('utf-8')
    log.debug("Data Received from wayback archive:" +
              "{0}".format(archive_data))
    parsed_data = json.loads(archive_data)
    snapshots = parsed_data['archived_snapshots']
    if len(snapshots) == 0:
        raise MissingArchiveError("No archive exists for the url" +
                                  " {0}".format(target_url))
    return snapshots

def get_archive_url(target_url, timestamp=None):
    """Get the url for an archived version of a url.
    """
    archive_info = get_archive_info(target_url, timestamp=timestamp)
    try:
        closest = archive_info['closest']
    except KeyError:
        raise MissingArchiveError("No archive exists for the url" +
                                  " {0}".format(target_url))
    archive_url = closest["url"]
    return archive_url

class MissingArchiveError(Exception):
    """Exception raised when an archive for a url does not exist."""
    pass

class RobotAccessControlException(Exception):
    """ Exception class for content blocked by robots.txt, etc.
    """
    pass

if __name__ == '__main__':
    pass
