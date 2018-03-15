#!/usr/bin/env python2.7
# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
""" Basic selenium test runner.
This script is used for running all selenium tests against the server defined
in the configuration yaml file. The script will wait a defined time for the
server to start before running the test. If the server fails to start before
its grace time is up, the script will return with an error code of 3. Error
codes 1 and 2 are reserved by pytest and status 0 is returned only if all the
tests pass.
"""

import os
import subprocess
import sys
import time

import _pytest
import requests

from lib import file_ops, environment, decorator  # noqa
from lib.service.rest_service import client


# add src to path so that we can do imports from our src
PROJECT_ROOT_PATH = os.path.dirname(os.path.abspath(__file__)) + "/../"
sys.path.append(PROJECT_ROOT_PATH + "src")


@decorator.track_time
def wait_for_server(url):
  """Wait for the server to return '200' status code in response during
  predefined time in 'pytest.ini'.
  """
  print "Wating on server: {}".format(url)
  for _ in xrange(environment.SERVER_WAIT_TIME):
    try:
      if (requests.head(url).status_code ==
              client.RestClient.STATUS_CODES["OK"]):
        return
    except IOError:
      time.sleep(1)
  print "Failed waiting for server {}".format(url)
  sys.exit(3)


def parse_pytest_ini():
  """# Initialize plugins, parse pytest.ini"""
  _pytest.config._prepareconfig()


def run_tests():
  """Plugins were already imported to this process by `parse_pytest_ini`.
  Running `pytest.main()` will cause them to be imported again and will produce
  a warning. So `pytest` is run in a subprocess.
  """
  sys.stdout.flush()  # Flush should be before calling a subprocess
  return subprocess.call("pytest")


if __name__ == "__main__":
  parse_pytest_ini()
  wait_for_server(os.environ["DEV_URL"])
  wait_for_server(os.environ["DEV_DESTRUCTIVE_URL"])
  file_ops.create_directory(environment.LOG_PATH)
  file_ops.delete_directory_contents(environment.LOG_PATH)
  #return_code = run_tests()
  #sys.exit(return_code)
