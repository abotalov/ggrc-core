# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Constants related to people objects"""

DEFAULT_EMAIL_DOMAIN = "example.com"
SUPERUSER_EMAIL = "user@" + DEFAULT_EMAIL_DOMAIN
MIGRATOR_USER_EMAIL = "migrator@" + DEFAULT_EMAIL_DOMAIN

UI_USER = "UI user"

_current_user = None  # pylint: disable=invalid-name
_logged_in_user_tracks = {}  # pylint: disable=invalid-name


def set_current_user(user):
  """Set user as the current user"""
  print "Set user: {}".format(user)
  # pylint: disable=invalid-name, global-statement
  global _current_user
  _current_user = user


def current_user():
  """Get current user"""
  return _current_user


def set_current_logged_in_user(track, user):
  """Set user as currently logged in via `track` (e.g. UI / REST)"""
  _logged_in_user_tracks[track] = user


def current_logged_in_user(track):
  """Return user that is currently logged in via `track` (e.g. UI / REST)"""
  if track not in _logged_in_user_tracks:
    return None
  return _logged_in_user_tracks[track]


def reset_logged_in_users():
  """Clear all currently logged in users, to be invoked before each test"""
  # pylint: disable=invalid-name, global-statement
  global _logged_in_user_tracks
  _logged_in_user_tracks = {}


class FakeSuperUser(object):
  """REST services perform requests under current_user.
  So current user should be set before using REST.
  """
  # pylint: disable=too-few-public-methods
  email = SUPERUSER_EMAIL
