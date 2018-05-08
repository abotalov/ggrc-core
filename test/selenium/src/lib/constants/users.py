# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Constants related to people objects"""
import sys

MIGRATOR_USER_EMAIL = "migrator@example.com"
DEFAULT_EMAIL_DOMAIN = "example.com"
SUPERUSER_EMAIL = "user@" + DEFAULT_EMAIL_DOMAIN
# CREATOR_EMAIL = "global_creator@" + DEFAULT_EMAIL_DOMAIN
# READER_EMAIL = "reader@" + DEFAULT_EMAIL_DOMAIN
# EDITOR_EMAIL = "editor@" + DEFAULT_EMAIL_DOMAIN
# ADMINISTRATOR_EMAIL = "administrator@" + DEFAULT_EMAIL_DOMAIN

users = {}
_current_user = None


def set_current_user(user):
  print "Set user: {}".format(user)
  sys.stdout.flush()
  global _current_user
  _current_user = user

def helper_function():
  print "qaz"

def get_current_user():
  return _current_user


def current_user_email():
  return _current_user.email
