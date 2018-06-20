# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Admin dashboard page smoke tests."""
# pylint: disable=no-self-use
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=protected-access

import random
import re

import pytest

from lib import base, constants, url, users
from lib.constants import objects, messages, roles
from lib.constants.element import AdminWidgetCustomAttributes
from lib.entities import entities_factory
from lib.page import dashboard
from lib.service import admin_webui_service
from lib.utils import selenium_utils


class TestAdminDashboardPage(base.Test):
  """Tests for admin dashboard page."""
  _role_el = constants.element.AdminWidgetRoles
  _event_el = constants.element.AdminWidgetEvents

  @pytest.fixture(scope="function")
  def admin_dashboard(self, selenium):
    """Open Admin Dashboard URL and
    return AdminDashboard page objects model."""
    selenium_utils.open_url(selenium, url.Urls().admin_dashboard)
    return dashboard.AdminDashboard(selenium)

  @pytest.mark.smoke_tests
  def test_roles_widget(self, admin_dashboard):
    """Check count and content of role scopes."""
    admin_roles_tab = admin_dashboard.select_roles()
    expected_dict = self._role_el.ROLE_SCOPES_DICT
    actual_dict = admin_roles_tab.get_role_scopes_text_as_dict()
    assert admin_dashboard.tab_roles.member_count == len(expected_dict)
    assert expected_dict == actual_dict, (
        messages.AssertionMessages.
        format_err_msg_equal(expected_dict, expected_dict))

  @pytest.mark.smoke_tests
  def test_events_widget_tree_view_has_data(self, admin_dashboard):
    """Confirms tree view has at least one data row in valid format."""
    admin_events_tab = admin_dashboard.select_events()
    list_items = [item.text for item in admin_events_tab.get_events()]
    assert list_items
    items_with_incorrect_format = [
        item for item in list_items if not
        re.compile(self._event_el.TREE_VIEW_ROW_REGEXP).match(item)]
    assert len(items_with_incorrect_format) in [0, 1]
    if len(items_with_incorrect_format) == 1:
      # A line with incorrect format is created during DB migration.
      # We decided it's OK.
      assert items_with_incorrect_format[0].startswith(
          "by\n{}".format(users.MIGRATOR_USER_EMAIL))
    expected_header_text = self._event_el.WIDGET_HEADER
    actual_header_text = admin_events_tab.widget_header.text
    assert expected_header_text == actual_header_text

  @pytest.mark.smoke_tests
  def test_check_ca_groups(self, admin_dashboard):
    """Check that full list of Custom Attributes groups is displayed
    on Admin Dashboard panel.
    """
    ca_tab = admin_dashboard.select_custom_attributes()
    expected_ca_groups_set = set(
        [objects.get_normal_form(item) for item in objects.ALL_CA_OBJS])
    actual_ca_groups_set = set(
        [item.text for item in ca_tab.get_items_list()])
    assert expected_ca_groups_set == actual_ca_groups_set

  @pytest.mark.smoke_tests
  @pytest.mark.parametrize(
      "ca_type",
      AdminWidgetCustomAttributes.ALL_CA_TYPES
  )
  def test_add_global_ca(self, admin_dashboard, ca_type):
    """Create different types of Custom Attribute on Admin Dashboard."""
    def_type = objects.get_normal_form(random.choice(objects.ALL_CA_OBJS))
    expected_ca = entities_factory.CustomAttributeDefinitionsFactory().create(
        attribute_type=ca_type, definition_type=def_type)
    ca_tab = admin_dashboard.select_custom_attributes()
    ca_tab.add_custom_attribute(ca_obj=expected_ca)
    actual_cas = ca_tab.get_custom_attributes_list(ca_group=expected_ca)
    # 'actual_ca': multi_choice_options (None)
    self.general_contain_assert(expected_ca, actual_cas,
                                "multi_choice_options")

  def test_create_new_person_w_no_role(self, selenium):
    """Check newly created person is on Admin People widget"""
    expected_person = entities_factory.PeopleFactory().create(
        system_wide_role=roles.NO_ROLE)
    actual_person = admin_webui_service.PeopleAdminWebUiService(
        selenium).create_new_person(expected_person)
    self.general_equal_assert(expected_person, actual_person)
