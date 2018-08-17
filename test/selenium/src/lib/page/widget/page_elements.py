# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Page objects for child elements of pages"""
# pylint: disable=too-few-public-methods

import re
import time


class RelatedPeopleList(object):
  """Represents related people element"""

  def __init__(self, container, acr_name):
    self._root = container.element(
        class_name="people-group__title", text=acr_name).parent(
            class_name="people-group")

  def add_person(self, person):
    """Add person to Related People list"""
    self._open_inline_edit()
    email = person.email
    self._root.text_field(placeholder="Add person").set(email)
    row = self._root.element(class_name="ui-menu-item", text=re.compile(email))
    row.click()
    self._confirm_inline_edit()

  def get_people_emails(self):
    """Get emails of people"""
    return [el.text for el in self._root.elements(class_name="person-name")]

  def _open_inline_edit(self):
    """Open inline edit"""
    # Hovering over element and clicking on it doesn't open the inline edit
    # control
    self._root.wait_until_present()
    self._root.element(class_name="set-editable-group").js_click()

  def _confirm_inline_edit(self):
    """Save changes via inline edit"""
    self._root.element(class_name="fa-check").click()
    # Wait for edit to save
    self._root.element(class_name="inline-edit").wait_until_not_present()
    time.sleep(1)  # wait for JS to work


class RelatedUrls(object):
  """Represents reference / evidence url section on info widgets"""

  def __init__(self, container, label):
    self._root = container.element(
        class_name="related-urls__title", text=label).parent(
            class_name="related-urls")
    self.add_button = self._root.button(class_name="related-urls__toggle")


class AssessmentEvidenceUrls(object):
  """Represents assessment urls section on info widgets"""

  def __init__(self, container):
    self._root = container.element(
        class_name="info-pane__section-title", text="Evidence URL").parent()

  def add_url(self, url):
    """Add url"""
    self._root.button(text="Add").click()
    self._root.text_field(class_name="create-form__input").set(url)
    self._root.element(class_name="create-form__confirm").click()

  def get_urls(self):
    """Get urls"""
    return [el.text for el in self._root.elements(class_name="link")]


class CommentArea(object):
  """Represents comment area (form and mapped comments) on info widget"""

  def __init__(self, container):
    self.add_section = container.element(
        class_name="comment-add-form__section")
