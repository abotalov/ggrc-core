# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Login page smoke tests."""
# pylint: disable=no-self-use
# pylint: disable=invalid-name

import pytest    # pylint: disable=import-error
from lib import base, url
from lib.constants import locator
from lib.utils import selenium_utils


class TestLoginPage(base.Test):

  @pytest.mark.smoke_tests
  def test_login_as_admin(self, selenium):
    """Logs in and verifies that we're logged in as admin."""
    selenium_utils.open_url(selenium, url.Urls().login)
    selenium.find_element(*locator.PageHeader.BUTTON_ADMIN_DASHBOARD)
