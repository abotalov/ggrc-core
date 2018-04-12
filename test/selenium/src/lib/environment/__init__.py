# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Import all settings from config files."""

import ConfigParser
import logging
import os
import urlparse

from lib import constants

PROJECT_ROOT_PATH = os.path.dirname(os.path.abspath(__file__)) + "/../../../"
VIRTENV_PATH = PROJECT_ROOT_PATH + constants.path.VIRTUALENV_DIR
LOG_PATH = PROJECT_ROOT_PATH + constants.path.LOGS_DIR


def _get_settings(path):
  "Get settings."
  settings = ConfigParser.ConfigParser()
  settings.read(path)
  return settings


def _set_loggers(settings):
  "Set loggers."
  logging_level = int(settings.get(
      constants.settings.Section.LOGGING, constants.settings.Values.LEVEL))
  selenium_logger = logging.getLogger(constants.log.SELENIUM_REMOTE_CONNECTION)
  selenium_logger.setLevel(logging_level)


_settings = _get_settings(PROJECT_ROOT_PATH + constants.path.CONFIG)
SERVER_WAIT_TIME = int(_settings.get(
    constants.settings.Section.APP,
    constants.settings.Values.WAIT_FOR_APP_SERVER))
RERUN_FAILED_TEST = int(_settings.get(
    constants.settings.Section.PYTEST,
    constants.settings.Values.RERUN_FAILED_TEST))

# register loggers
_set_loggers(_settings)
