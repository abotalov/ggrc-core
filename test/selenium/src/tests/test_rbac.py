# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for RBAC"""
# pylint: disable=no-self-use

import pytest

from lib import base, users
from lib.constants import roles
from lib.service import rest_facade, webui_facade


class TestRBAC(base.Test):
  """Tests for RBAC"""

  ALL_ROLES = [roles.CREATOR, roles.READER, roles.EDITOR, roles.ADMINISTRATOR]

  @pytest.fixture()
  def users_with_all_roles(self):
    return {role: rest_facade.create_user_with_role(role_name=role)
            for role in self.ALL_ROLES}

  @pytest.mark.smoke_tests
  @pytest.mark.parametrize(
      "role",
      [roles.CREATOR, roles.READER, roles.EDITOR]
  )
  def test_object_creation(self, role, selenium):
    """Test that users with all global roles can create, then edit and delete
    objects.
    """
    user = rest_facade.create_user_with_role(role_name=role)
    users.set_current_user(user)
    objs = [rest_facade.create_program(), rest_facade.create_control()]
    for obj in objs:
      webui_facade.assert_can_edit(selenium, obj, can_edit=True)
      webui_facade.assert_can_delete(selenium, obj, can_delete=True)

  @pytest.mark.smoke_tests
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
  ):  # pylint: disable=too-many-arguments
    """Test that users have permissions to objects created by other users
    according to their global role.
    """
    objs = []
    other_roles = [role for role in self.ALL_ROLES if role != login_role]
    for role in other_roles:
      users.set_current_user(users_with_all_roles[role])
      program = rest_facade.create_program()
      control = rest_facade.create_control(program)
      objs.extend([program, control])
    users.set_current_user(users_with_all_roles[login_role])
    for obj in objs:
      if can_view:
        webui_facade.assert_can_view(selenium, obj)
        webui_facade.assert_can_edit(selenium, obj, can_edit=can_edit)
        webui_facade.assert_can_delete(selenium, obj, can_delete=can_edit)
      else:
        webui_facade.assert_cannot_view(selenium, obj)

  @pytest.mark.smoke_tests
  def test_auditor_cannot_edit_audit(self, selenium):
    """Test that Auditor cannot edit audit"""
    editor = rest_facade.create_user_with_role(roles.EDITOR)
    creator = rest_facade.create_user_with_role(roles.CREATOR)
    users.set_current_user(editor)
    program = rest_facade.create_program()
    control = rest_facade.create_control(program=program)
    audit = rest_facade.create_audit(program, auditors=[creator])
    users.set_current_user(creator)
    webui_facade.assert_can_view(selenium, audit)
    webui_facade.assert_can_edit(selenium, audit, can_edit=False)
    webui_facade.assert_cannot_view(selenium, control)
