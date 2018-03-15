# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests that can't be run in parallel with other tests."""

import os
import pytest

from lib import base, environment
from lib.constants import objects
from lib.page.widget import generic_widget


@pytest.fixture(scope="function", autouse=True)
def dev_destructive_url():
  """Return a base URL."""
  environment.APP_URL = os.environ["DEV_DESTRUCTIVE_URL"]
  if not environment.APP_URL.endswith("/"):
    environment.APP_URL += "/"
  return environment.APP_URL


@pytest.mark.destructive
class TestMyWorkPage(base.Test):
  """Tests My Work page, part of smoke tests, section 2."""

  @pytest.mark.smoke_tests
  def test_horizontal_nav_bar_tabs(self, new_controls_rest, my_work_dashboard,
                                   selenium):
    """Tests that several objects in widget can be deleted sequentially.
    Preconditions:
    - Controls created via REST API.
    """
    controls_tab = my_work_dashboard.select_controls()
    for _ in xrange(controls_tab.member_count):
      counter = controls_tab.get_items_count()
      (controls_tab.select_member_by_num(0).
       open_info_3bbs().select_delete().confirm_delete())
      controls_tab.wait_member_deleted(counter)
    controls_generic_widget = generic_widget.Controls(
        selenium, objects.CONTROLS)
    expected_widget_members = []
    actual_widget_members = controls_generic_widget.members_listed
    assert expected_widget_members == actual_widget_members
