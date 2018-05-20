# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from ggrc import db
from ggrc_basic_permissions.models import Role


def _find_basic(role_name):
  return db.session.query(Role).filter(Role.name == role_name).first()

# System Roles


def reader():
  return _find_basic('Reader')


def creator():
  return _find_basic('Creator')


def editor():
  return _find_basic('Editor')
