# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for RBAC"""
import pytest

from lib import base
from lib.constants import roles, users
from lib.service import rest_facade, webui_facade


class TestRBAC(base.Test):

  # @pytest.fixture()
  # def ui_program(self):
  #   # BAD!
  #   ui_facade.login_if_needed().create_obj("Program")

  # @pytest.fixture()
  # def global_creator_ui_program(self, set_user_global_creator, ui_program):
  #   return ui_program

  ALL_ROLES = [roles.CREATOR, roles.READER, roles.EDITOR, roles.ADMINISTRATOR]

  @pytest.fixture()
  def users_with_all_roles(self):
    return {role: rest_facade.create_user_with_role(role_name=role)
            for role in self.ALL_ROLES}

  @pytest.mark.parametrize(
    "login_role, can_view, can_edit",
    [
      (roles.CREATOR, False, False),
      (roles.READER, True, False),
      (roles.EDITOR, True, True)
    ]
  )
  def test_permissions(
    self, users_with_all_roles, login_role, can_view, can_edit, selenium
  ):
    objs = []
    roles = [role for role in self.ALL_ROLES if role != login_role]
    for role in roles:
      users.set_current_user(users_with_all_roles[role])
      program = rest_facade.create_program()
      control = rest_facade.create_control(program)
      objs.extend([program, control])
    users.set_current_user(users_with_all_roles[login_role])
    for obj in objs:
      webui_facade.assert_can_view(selenium, obj, can_view=can_view)
    if can_view:
      for obj in objs:
        webui_facade.assert_can_edit(selenium, obj, can_edit=can_edit)
      for obj in objs:
        webui_facade.assert_can_delete(selenium, obj)

  # Procedural
  # def test():
  #   users.set_user(users.GLOBAL_EDITOR)
  #   program = rest_facade.create_program()
  #   control = rest_facade_create_control()
  #   audit = rest_facade.create_audit(program, audit_captain=users.GLOBAL_CREATOR)
  #   users.set_user(global_creator)
  #   assert ui_facade.can_access(obj) == False
  #   assert ui_facade.can_access(obj) == False
