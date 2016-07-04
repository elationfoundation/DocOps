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
from collections import namedtuple
import json
import time

import logging
logging.basicConfig(level=logging.ERROR)
log = logging.getLogger(__name__)

class Archive(object):
    """

    :returns:  object

    http://timetravel.mementoweb.org/guide/api/
    http://www.mementoweb.org/guide/quick-intro/
    http://examinemint.com/about-the-time-travel-service/
    """

    def __init__(self, target_url, submission_url="http://web.archive.org/save/", request_url="http://timetravel.mementoweb.org/api/json/"):
        """
        :param target_url: The url that will be
        :type name: str.
        :param submission_url: The url used to submit links for archiving.
        :type name: str.
        :param request_url: The url used to request archive information about a link.
        :type name: str.
        """
        self.raw = None
        self.mementos = None
        self.sources = namedtuple("source", ["target", "submission", "request"])
        self.sources.target = target_url
        self.sources.submission = submission_url
        self.sources.request = request_url

    def request(self):
        """ Request an archive's url

        :raises: ValueError
        :returns:  str -- The URI of an archive for the target URI.
        """
        if self.mementos is None:
            self.find()

        archive_versions = ["closest", "previous", "next", "last", "first"]
        for version in archive_versions:
            memento = self.mementos.get(version, {})
            memento_uri = memento.get("uri", None)
            if memento_uri is not None:
                break

        if memento_uri is None:
            raise ValueError("No archived versions can be found")
        # Return the first link in the uri array.
        return memento_uri[0]

    def submit(self):
        """Submit a url to be archived

        :raises: RobotAccessControlException, MissingArchiveError
        """
        try:
            # Submit the url
            urlopen(self.sources.submission + self.sources.target)
        except HTTPError as e:
            response_info = e.info()
            wayback_error = response_info.get('X-Archive-Wayback-Runtime-Error', None)
            if wayback_error is None:
                log.debug("Unknown HTTP error occurred")
                raise UnknownArchiveException(response_info)
            else:
                archive_error = wayback_error.split(":")[0]
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


    def find(self, timestamp=None):
        """Get archive information for an archived item from the time travel service

        :param target_url: A desired datetime you wish the targeted URI to be close to. The format of the timestamp is 1-14 digits (YYYYMMDDhhmmss)
        :type name: str.
        :raises: NotImplementedError, ValueError, MissingArchiveError

        Timetravel API: http://timetravel.mementoweb.org/guide/api

        Example response from timetravel server.
            {"original_uri": "http://seamustuohy.com/",
             "mementos":{
                 "last":{"datetime":"2016-03-27T20:26:13Z",
                         "uri":["http://web.archive.org/web/20160327202613/http://seamustuohy.com/"]},
                 "next":{"datetime":"2015-08-01T22:39:21Z",
                         "uri":["http://web.archive.org/web/20150801223921/http://seamustuohy.com/"]},
                 "closest":{"datetime":"2015-08-01T22:39:20Z",
                            "uri":["http://web.archive.org/web/20150801223920/http://seamustuohy.com/"]},
                 "first":{"datetime":"2015-08-01T22:39:20Z",
                          "uri":["http://web.archive.org/web/20150801223920/http://seamustuohy.com/"]}},
             "timegate_uri":"http://timetravel.mementoweb.org/timegate/http://seamustuohy.com/",
             "timemap_uri":{"json_format":"http://timetravel.mementoweb.org/timemap/json/http://seamustuohy.com/",
                            "link_format":"http://timetravel.mementoweb.org/timemap/link/http://seamustuohy.com/"}}
        """

        # Request URL
        # http://timetravel.mementoweb.org/memento/YYYY<MM|DD|HH|MM|SS>/URI
        if timestamp is None:
            time_query = self.sources.request + time.strftime("%Y") + "/"
        else:
            valid_datetimes = ["%Y",
                               "%Y%m",
                               "%Y%m%d",
                               "%Y%m%d%H",
                               "%Y%m%d%H%M",
                               "%Y%m%d%H%M%s"]
            valid_timestamp = False
            for parse_string in valid_datetimes:
                try:
                    valid_timestamp = time.strptime(parse_string)
                except ValueError:
                    continue

            # If the timestamp has not been set as valid error out
            if valid_timestamp is False:
                raise ValueError("timestamp {0} is not in a valid format.")
            else:
                time_query = self.sources.request + timestamp + "/"

        archive_query = time_query + self.sources.target

        try:
            mementos = self._get_archive_json(archive_query)
        except ValueError:
            # Occasionally it will return the HTML instead
            # so we sleep and try once more
            time.sleep(1)
            mementos = None
        if mementos is None:
            try:
                mementos = self._get_archive_json(archive_query)
            except ValueError:
                pass
        self.mementos = mementos


    def _get_archive_json(self, archive_query):
        try:
            archive_check = urlopen(archive_query)
        except HTTPError as e:
            if e.code == 404:
                raise MissingArchiveError("No archive exists for the url" +
                                          " {0}".format(self.sources.target))
            else:
                raise NotImplementedError("Archive encountered an error " +
                                          "it was not prepared to handle " +
                                          "when processing {0}".format(self.sources.target))
        archive_query = archive_check.read()
        archive_data = archive_query.decode('utf-8')
        log.debug("Data Received from wayback archive:" +
                  "{0}".format(archive_data))
        self.raw = archive_data

        # Parse Data
        parsed_data = json.loads(self.raw)
        return parsed_data['mementos']


class MissingArchiveError(Exception):
    """Exception raised when an archive for a url does not exist."""
    pass

class RobotAccessControlException(Exception):
    """ Exception class for content blocked by robots.txt, etc."""
    pass

class UnknownArchiveException(Exception):
    """Exception raised when an archive for a url does not exist."""
    pass
