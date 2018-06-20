# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Facade for Web UI services"""
import copy
import re

import nerodia

from lib import users, base
from lib.constants import objects
from lib.service import webui_service, rest_service
from lib.utils import selenium_utils


def create_program(selenium):
  """Create program via UI"""
  return webui_service.ProgramsService(selenium).create_obj()


def create_control(selenium):
  """Create control via UI"""
  return webui_service.ControlsService(selenium).create_obj()


def assert_can_view(selenium, obj):
  """Assert that current user can view object via UI.
  We go through all elements of the page in order to check that user
  has access to them.
  """
  _get_ui_service(selenium, obj).get_obj_from_info_page(obj)
  actual_obj = _get_ui_service(selenium, obj).get_obj_from_info_page(obj)
  obj_copy = copy.deepcopy(obj)
  # Code for working with custom attributes appeares to be buggy
  base.Test.general_equal_assert(
      obj_copy.repr_ui(), actual_obj, "custom_attributes", "program")


def assert_cannot_view(selenium, obj):
  """Assert that current user cannot view object via UI"""
  selenium_utils.open_url(selenium, obj.url)
  assert is_error_403(selenium)


def assert_can_edit(selenium, obj, can_edit):
  """If `can_edit` is True, assert that current user can edit object via UI
  otherwise check that user cannot edit object via UI
  """
  ui_service = _get_ui_service(selenium, obj=obj)
  info_page = ui_service.open_info_page_of_obj(obj)
  els_shown_for_editor = info_page.els_shown_for_editor()
  assert [item.exists for item in els_shown_for_editor] == \
         [can_edit] * len(els_shown_for_editor)
  if can_edit:
    _assert_title_editable(obj, ui_service, info_page)


def assert_can_delete(selenium, obj, can_delete):
  """If `can_delete` is True, assert that current user can delete object via UI
  otherwise check that user cannot delete object via UI
  """
  info_page = _get_ui_service(selenium, obj=obj).open_info_page_of_obj(obj)
  assert info_page.info_3bbs_btn.exists == can_delete
  if can_delete:
    info_page.open_info_3bbs().select_delete().confirm_delete()
    selenium_utils.open_url(selenium, obj.url)
    assert is_error_404(selenium)


def _get_ui_service(selenium, obj):
  """Get webui_service for object"""
  obj_type = objects.get_plural(obj.type)
  return webui_service.BaseWebUiService(selenium, obj_type)


def _assert_title_editable(obj, ui_service, info_page):
  """Assert that user can edit object's title"""
  new_title = "[EDITED]" + obj.title
  info_page.open_info_3bbs().select_edit().edit_minimal_data(
      title=new_title).save_and_close()
  obj.update_attrs(
      title=new_title, modified_by=users.current_user().email,
      updated_at=rest_service.ObjectsInfoService().get_obj(
          obj=obj).updated_at)
  new_ui_obj = ui_service.get_obj_from_info_page(obj)
  base.Test.general_equal_assert(
      obj.repr_ui(), new_ui_obj, "custom_attributes")


def is_error_403(selenium):
  """Return whether current page is 403 error"""
  return _browser(selenium).h1(visible_text="Forbidden").exists


def is_error_404(selenium):
  """Return whether current page is 404 error"""
  return _browser(selenium).body(visible_text=re.compile("not found")).exists


def _browser(driver):
  """Return nerodia browser for the driver"""
  return nerodia.browser.Browser(browser=driver)
