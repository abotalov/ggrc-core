# -*- coding: utf-8 -*-
# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Control object review workflow tests."""
# pylint: disable=no-self-use
# pylint: disable=invalid-name
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=redefined-outer-name
import re
import pytest
from lib import base, constants
from lib.entities.entities_factory import PeopleFactory
from lib.service import webui_service, rest_service
from lib.utils import string_utils


class TestControlsWorkflow(base.Test):
  """Test class for control scenario tests"""
  info_service = rest_service.ObjectsInfoService
  usr_email = PeopleFactory.superuser.name
  rand_msg = string_utils.StringMethods.random_string()

  def _assert_control(self, actual_control, new_control_rest):
    """Assert control object on equeals."""
    self.general_equal_assert(new_control_rest.repr_ui(), actual_control,
                              "created_at", "updated_at",
                              "custom_attribute_definitions",
                              "custom_attributes",
                              "object_review_txt")

  @pytest.mark.parametrize(
      "action, exp_message, regex, os_sate, review_param",
      [("approve_review", "REVIEWED BY\n{}\nON",
        constants.element.Common.APPROVED_DATE_REGEX, "Reviewed", []),
       ("decline_review", "Review was declined on ",
        constants.element.Common.DECLINED_DATE_REGEX, "Unreviewed",
          [rand_msg])])
  def test_control_review_flow(self, new_control_rest, action, exp_message,
                               regex, os_sate, review_param, selenium):
    """Test accept review scenario"""
    control_ui_service = webui_service.ControlsService(selenium)
    control_ui_service.open_info_page_of_obj(new_control_rest)
    control_ui_service.submit_obj_for_review(new_control_rest,
                                             self.usr_email)
    getattr(control_ui_service, action)(new_control_rest, *review_param)
    actual_control = control_ui_service.get_obj_from_info_page(
        new_control_rest)
    new_control_rest.update_attrs(os_state=os_sate)

    full_regex = unicode(exp_message.format(self.usr_email.upper())) + regex
    self._assert_control(actual_control, new_control_rest)
    assert re.compile(full_regex).match(actual_control.object_review_txt)
