# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Page objects for child elements of pages"""
# pylint: disable=too-few-public-methods


class RelatedUrls(object):
  """Represents reference / evidence url section on info widgets"""

  def __init__(self, descendant_el, label):
    self._root = descendant_el.element(
        class_name="related-urls__title", text=label).parent(
            class_name="related-urls")
    self.add_button = self._root.button(class_name="related-urls__toggle")


class CommentArea(object):
  """Represents comment area (form and mapped comments) on info widget"""

  def __init__(self, descendant_el):
    self.add_section = descendant_el.element(
        class_name="comment-add-form__section")
