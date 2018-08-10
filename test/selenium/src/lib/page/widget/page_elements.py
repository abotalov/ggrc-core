# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Page objects for child elements of pages"""
# pylint: disable=too-few-public-methods
import datetime
import re

from lib import users
from lib.constants.element import AdminWidgetCustomAttributes

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
    autocomplete_row = self._root.element(
        class_name="ui-menu-item", text=re.compile(email))
    autocomplete_row.click()
    self._confirm_inline_edit()

  def get_people_emails(self):
    """Get emails of people"""
    return [el.text for el in self._root.elements(class_name="person-name")]

  def _open_inline_edit(self):
    """Open inline edit"""
    # Hovering over element and clicking on it using Selenium / Nerodia
    # doesn't open the inline edit control for some reason
    self._root.wait_until_present()
    self._root.element(class_name="set-editable-group").js_click()

  def _confirm_inline_edit(self):
    """Save changes via inline edit"""
    self._root.element(class_name="fa-check").click()
    # Wait for inline edit element to be removed
    self._root.element(class_name="inline-edit").wait_until_not_present()
    # Wait for JS to work, there are no DOM changes and HTTP requests
    # during some period (GGRC-5891).
    # Sleep is actually needed only for saving ACL roles on assessment page
    time.sleep(1)


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


class CustomAttributeManager(object):
  """Represents manager class to define CAS element based on its type."""

  def __init__(self, browser):
    self._label = None
    self._type = None
    self._browser = browser
    self._all_types = {
        AdminWidgetCustomAttributes.TEXT: InputFieldCAElem,
        AdminWidgetCustomAttributes.RICH_TEXT: TextCAElem,
        AdminWidgetCustomAttributes.DATE: DateCAElem,
        AdminWidgetCustomAttributes.CHECKBOX: CheckboxCAElem,
        AdminWidgetCustomAttributes.DROPDOWN: DropdownCAElem,
        AdminWidgetCustomAttributes.PERSON: PersonCAElem
    }

  def get_attr_elem_class(self, attr):
    """Returns custom attribute element class."""
    self._label = attr.title
    self._type = attr.attribute_type
    elem = self._all_types[self._type](self._browser, self._label)
    return elem

class CustomAttributeScope(object):

  def __init__(self, browser):
    self.cas_scopes = browser.element(class_name=re.compile(
          'ggrc-form-item')).elements(
        tag_name='inline-edit-control')
    self.lcas_scopes = browser.element(
      class_name='custom-attributes').elements(
          tag_name='div', class_name=re.compile("custom-attribute"))


  def get_cas_scopes(self, is_lcas_not_gcas):
    return self.lcas_scopes if is_lcas_not_gcas else self.cas_scopes


class CustomAttribute(object):
  """Represents all customa attribute parent class,
  which knows and controls root element for each custom element"""

  def __init__(self, browser, label):
    self._label_txt = label.encode('UTF-8')
    self._label_popup = browser.element(
        class_name=re.compile("label-text"), text=self._label_txt)
    self._label_inline = browser.element(
        tag_name='div', class_name=re.compile(
            "title"), text=re.compile(
            re.escape(self._label_txt), re.IGNORECASE))
    self._root_gcas_popup = self._label_popup.parent(
        class_name=re.compile('ggrc-form-item__row'))
    self._root_gcas_inline = self._label_inline.parent(
        class_name=re.compile("ggrc-form-item__"))
    self._root_lcas_inline = self._label_inline.parent(
        class_name=re.compile("fields-wrapper"))
    self._root = self.init_root()

  def init_root(self):
    """Defines elements root based on current page"""
    if self._label_popup.exists:
      return self._root_gcas_popup
    elif self._label_inline.exists:
      if self._root_gcas_inline.exists:
        return self._root_gcas_inline
      elif self._root_lcas_inline.exists:
        return self._root_lcas_inline
      else:
        raise NotImplementedError
    else:
      raise NotImplementedError

  def get_gcas_from_inline(self):
    pass

  def set_lcas_from_inline(self, value):
    pass

  def get_lcas_from_inline(self):
    pass

  def set_gcas_from_popup(self, value):
    pass


class DateCAElem(CustomAttribute):
  """Representation for Date custom attribute"""

  def __init__(self, browser, label):
    super(DateCAElem, self).__init__(browser, label)
    self._datepicker_field = self._root.element(
        class_name="datepicker__input date ")
    self._datepicker_opts = self._root.element(
        class_name="datepicker__calendar").elements(
        data_handler='selectDay')
    self._input_blank_inline = self._root.element(
        class_name="empty-message")
    self._input_existent_inline = self._root.element(
        class_name="inline-edit__text")

  def get_gcas_from_inline(self):
    """Retrieves global custom attribute from UI"""
    return (
        None if self._input_blank_inline.exists
        else self._input_existent_inline.text
    )

  def set_lcas_from_inline(self, value):
    self._select_date(value)

  def get_lcas_from_inline(self):
    return self._datepicker_field.value

  def set_gcas_from_popup(self, value):
    self._select_date(value)

  def _select_date(self, value):
    """Select day in current month"""
    self._datepicker_field.click()
    self._datepicker_opts[
        datetime.datetime.strptime(value, "%Y-%m-%d").day - 1].click()


class TextCAElem(CustomAttribute):
  """Representation for Date custom attribute"""

  def __init__(self, browser, label):
    super(TextCAElem, self).__init__(browser, label)
    self._input_blank_gcas_inline = self._root.element(
        class_name="empty-message")
    self._input_existent_gcas_inline = self._root.element(
        tag_name='div', class_name="read-more__body ellipsis-truncation-5")
    self._input_blank = self._root.element(
        class_name="ql-editor ql-blank")
    self._input_existent_lcas_inline = self._root.element(
        class_name=re.compile("rich-text__content"))

  def get_gcas_from_inline(self):
    return (
        None if self._input_blank_gcas_inline.exists
        else self._input_existent_gcas_inline.text
    )

  def set_lcas_from_inline(self, value):
    self._input_blank.send_keys(value)

  def get_lcas_from_inline(self):
    return(
        None if self._input_blank.exists
        else self._input_existent_lcas_inline.text
    )

  def set_gcas_from_popup(self, value):
    self._input_blank.send_keys(value)


class InputFieldCAElem(CustomAttribute):
  """Representation for Input field custom attribute"""

  def __init__(self, browser, label):
    super(InputFieldCAElem, self).__init__(browser, label)
    self._input_blank_inline_gcas = self._root.element(
        class_name="empty-message")
    self._input_existent_inline_gcas = self._root.element(
        class_name="read-more__body ellipsis-truncation-5").div()
    self._input_blank = self._root.text_field(
        class_name="text-field")

  def get_gcas_from_inline(self):
    return (
        None if self._input_blank_inline_gcas.exists
        else self._input_existent_inline_gcas.text
    )

  def set_lcas_from_inline(self, value):
    self._input_blank.send_keys(value)

  def get_lcas_from_inline(self):
    return self._input_blank.value

  def set_gcas_from_popup(self, value):
    self._input_blank.send_keys(value)


class CheckboxCAElem(CustomAttribute):
  """Representation for Checkbox custom attribute"""

  def __init__(self, browser, label):
    super(CheckboxCAElem, self).__init__(browser, label)
    self._input = self._root.checkbox(type='checkbox')

  def get_gcas_from_inline(self):
    return self._input.checked

  def set_lcas_from_inline(self, value):
    if value:
      self._input.click()

  def get_lcas_from_inline(self):
    return self._input.checked

  def set_gcas_from_popup(self, value):
    if value:
      self._input.click()


class DropdownCAElem(CustomAttribute):
  """Representation for Dropown custom attribute"""

  def __init__(self, browser, label):
    super(DropdownCAElem, self).__init__(browser, label)
    self._input = self._root.select(class_name="input-block-level")

  def get_gcas_from_inline(self):
    return self._input.value

  def set_lcas_from_inline(self, value):
    self._input.select(value)

  def get_lcas_from_inline(self):
    return self._input.value

  def set_gcas_from_popup(self, value):
    self._input.select(value)


class PersonCAElem(CustomAttribute):
  """Representation for Person custom attribute"""

  def __init__(self, browser, label):
    super(PersonCAElem, self).__init__(browser, label)
    self._input = self._root.text_field(data_lookup='Person')
    self._input_existent = self._root.element(tag_name='person-data')
    self._input_opts = self._root.element(class_name='ui-menu-item')
    self._input_empty_msg_gcas = self._root.element(
        class_name="empty-message")
    self._input_exist_msg = self._root.element(
        class_name="person-name")

  def get_gcas_from_inline(self):
    return (
        None if self._input_empty_msg_gcas.exists
        else self._input_exist_msg.text
    )

  def set_lcas_from_inline(self, value):
    self._input.send_keys(value)
    self._input_opts.click()

  def get_lcas_from_inline(self):
    return (
        self._input.value if self._input.exists
        else self._input_exist_msg.text
    )

  def set_gcas_from_popup(self, value):
    self._input.send_keys(value)
    self._input_opts.click()
