# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Mixins for info page objects"""
# pylint: disable=too-few-public-methods

from lib import base
from lib.page.widget import page_elements


class WithPageElements(base.WithBrowser):
  """A mixin for page elements"""

  def _related_urls(self, label):
    """Return RelatedUrls page element with label `label`"""
    return page_elements.RelatedUrls(self._browser, label)

  def _comment_area(self):
    """Return CommentArea page element"""
    return page_elements.CommentArea(self._browser)


class WithAssignFolder(base.WithBrowser):
  """A mixin for `Assign Folder`"""

  def __init__(self, driver):
    super(WithAssignFolder, self).__init__(driver)
    self.assign_folder_button = self._browser.element(
        class_name="mapped-folder__add-button")


class WithObjectReview(base.WithBrowser):
  """A mixin for object reviews"""

  def __init__(self, driver):
    super(WithObjectReview, self).__init__(driver)
    self.submit_for_review_link = self._browser.link(text="Submit For Review")
