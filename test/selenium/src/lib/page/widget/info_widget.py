# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Info widgets."""
# pylint: disable=useless-super-delegation

import re

from selenium.webdriver.common.by import By

from lib import base, users
from lib.constants import (
    locator, objects, element, roles, regex, messages)
from lib.constants.locator import WidgetInfoAssessment, WidgetInfoControl
from lib.element import widget_info, tab_containers, tables
from lib.page.modal import update_object
from lib.page.modal.set_value_for_asmt_ca import SetValueForAsmtDropdown
from lib.page.widget import page_tab
from lib.page.widget.page_mixins import (WithAssignFolder, WithObjectReview,
                                         WithPageElements)
from lib.utils import selenium_utils, string_utils, help_utils


class InfoWidget(page_tab.WithPageTab, WithPageElements, base.Widget):
  """Abstract class of common info for Info pages and Info panels.
  For labels (headers) Will be used actual unicode elements from UI or pseudo
  string elements from 'lib.element' module in upper case.
  """
  # pylint: disable=too-many-instance-attributes
  # pylint: disable=protected-access
  _locators = locator.CommonWidgetInfo
  _elements = element.Common
  dropdown_settings_cls = widget_info.CommonInfoDropdownSettings
  locator_headers_and_values = None
  _reference_url_label = "Reference URL"
  _evidence_url_label = "Evidence URL"

  def __init__(self, driver):
    super(InfoWidget, self).__init__(driver)
    self.child_cls_name = self.__class__.__name__
    self.is_asmts_info_widget = (
        self.child_cls_name.lower() == objects.ASSESSMENTS)
    self.list_all_headers_txt = []
    self.list_all_values_txt = []
    self.info_widget_locator = (
        self._locators.INFO_PAGE_ELEM if self.is_info_page else
        self._locators.INFO_PANEL_ELEM)
    self.info_widget_elem = selenium_utils.get_when_visible(
        self._driver, self.info_widget_locator)
    # common for all objects
    self.title = base.Element(
        self.info_widget_elem, self._locators.TITLE_ENTERED)
    self.state_lbl_txt = self._elements.STATE.upper()
    self.state_txt = self.get_state_txt()
    self._extend_list_all_scopes(
        ["TITLE", self.state_lbl_txt],
        [self.title.text, self.state_txt])
    self.info_3bbs_btn = self._browser.element(
        xpath=self._locators.BUTTON_3BBS_XPATH)
    self.inline_edit_controls = self._browser.elements(
        class_name="set-editable-group")
    # for Info Page
    if self.is_info_page:
      self.info_page_footer = base.Label(
          self.info_widget_elem, self._locators.TXT_FOOTER_CSS)
      self.modified_by = selenium_utils.get_when_visible(
          self.info_widget_elem, self._locators.TXT_MODIFIED_BY_CSS)
      _created_at_txt, _updated_at_txt = (
          self.info_page_footer.text.split(
              string_utils.Symbols.WHITESPACE * 6))
      self.created_at_txt = (
          re.sub(element.Common.CREATED_AT, string_utils.Symbols.BLANK,
                 _created_at_txt))
      self.updated_at_txt = (
          _updated_at_txt.splitlines()[2].replace(
              "on ", string_utils.Symbols.BLANK))
      self._extend_list_all_scopes(
          [self._elements.CREATED_AT.upper(),
           self._elements.MODIFIED_BY.upper(),
           self._elements.UPDATED_AT.upper()],
          [self.created_at_txt, self.modified_by.text, self.updated_at_txt])
    # for Info Panel
    else:
      self.panel = (
          SnapshotedInfoPanel(self._driver, self.info_widget_elem)
          if (self.child_cls_name.lower() in objects.ALL_SNAPSHOTABLE_OBJS and
              self.is_snapshoted_panel) else
          InfoPanel(self._driver, self.info_widget_elem))
    # for tab controller
    if not self.is_snapshoted_panel:
      self.tab_container_elem = self.info_widget_elem.find_element(
          *self._locators.TAB_CONTAINER_CSS)
      self.tab_container = (
          tab_containers.AssessmentsTabContainer(
              self._driver, self.tab_container_elem) if
          self.is_asmts_info_widget else tab_containers.TabContainer(
              self._driver, self.tab_container_elem))
      self.tab_container.tab_controller.active_tab = (
          self.tab_container._elements.OBJ_TAB)
    # core element to find sub elements
    self.core_elem = (self.info_widget_elem if self.is_snapshoted_panel else
                      self.tab_container.active_tab_elem)
    # for overridable methods
    self._extend_list_all_scopes_by_review_state()
    if not self.is_asmts_info_widget:
      self._extend_list_all_scopes_by_code()
      self._extend_list_all_scopes_by_cas()
    self.comment_area = self.comment_area()

  def wait_save(self):
    """Wait for object to be saved and page to be updated.
    Please note that in some cases spinner disappears before DOM changes
    are fully finished. So this code may need to be changed
    in case of a race condition.
    """
    self._browser.element(class_name="spinner").wait_until_not_present()
    # self._browser.execute_script("""
    #   window.__events = [];
    #   observer = new MutationObserver(function(mutations) {
    #       mutations.forEach(function(mutation) {
    #           window.__events.push(mutation.type);
    #       });
    #   })
    #   observer.observe(document.body, {childList: true, subtree: true})
    # """)
    # t = datetime.datetime.now()
    # a = self._driver.execute_async_script("""
    #   var callback = arguments[arguments.length - 1];
    #   var events = [];
    #   observer = new MutationObserver(function(mutations) {
    #       mutations.forEach(function(mutation) {
    #           events.push(mutation.type);
    #       });
    #   })
    #   observer.observe(document.body, {childList: true, subtree: true});
    #   var prev_events = [];
    #   var check = function(n) {
    #       if (events.length - prev_events.length == 0) {
    #           callback('good');
    #       } else if (n < 1) {
    #           callback('timeout');
    #       } else {
    #           prev_events = events.slice();
    #           setTimeout(function() {check(n - 1);}, 500);
    #       }
    #   };
    #   setTimeout(function() {check(10);}, 500);
    #  """)
    # t2 = datetime.datetime.now()
    # time.sleep(2)  # wait for first DOM changes
    # prev_records = [[]]
    #
    # def some_records():
    #   new_records = self._browser.execute_script("return window.__events;")
    #   if len(new_records) - len(prev_records[0]) > 0:
    #     prev_records[0] = new_records
    #     return False
    #   else:
    #     return True
    # test_utils.wait_for(some_records, sleep_seconds=0.3)

  def get_state_txt(self):
    """Get object's state text from Info Widget."""
    return objects.get_normal_form(
        base.Label(self.info_widget_elem, self._locators.STATE).text)

  def get_review_state_txt(self):
    """Get object's review state text from Info Widget checking if exact UI
    elements are existed.
    """
    return (element.ReviewStates.REVIEWED if selenium_utils.is_element_exist(
        self.info_widget_elem, self._locators.TXT_OBJECT_REVIEWED) else
        element.ReviewStates.UNREVIEWED)

  def show_related_assessments(self):
    """Click `Assessments` button on control or objective page and return
    related asmts table.
    """
    base.Button(self.info_widget_elem,
                self._locators.SHOW_RELATED_ASSESSMENTS).click()
    table_element = self._driver.find_element(
        *locator.ModalRelatedAssessments.MODAL)
    return tables.AssessmentRelatedAsmtsTable(self._driver, table_element)

  def open_info_3bbs(self):
    """Click to 3BBS button on Info page or Info panel to open info 3BBS modal.
    Return: lib.element.widget_info."obj_name"DropdownSettings
    """
    self.info_3bbs_btn.click()
    return self.dropdown_settings_cls(self._driver)

  def get_header_and_value_txt_from_custom_scopes(self, header_text):
    """Get one header and one value elements text from custom scopes elements
    according to header text.
    Example:
    If header_text is 'header' :return ['header', 'value']
    """
    # pylint: disable=not-an-iterable
    # pylint: disable=invalid-name
    selenium_utils.wait_for_js_to_load(self._driver)
    all_headers_and_values = self.core_elem.find_elements(
        *self._locators.HEADERS_AND_VALUES)
    return next((scope.text.splitlines() + [None]
                 if len(scope.text.splitlines()) == 1
                 else scope.text.splitlines()[:2]
                 for scope in all_headers_and_values
                 if header_text in scope.text), [None, None])

  def get_header_and_value_txt_from_people_scopes(self, header_text):
    """Get with controlling header and value text from people's scopes elements
    according to header text.

    Example:
    'header_text' = 'ASSIGNEE(S)', return: ['ASSIGNEE(S)', 'user@example.com']
    """
    # pylint: disable=invalid-name
    # pylint: disable=expression-not-assigned
    _header_msg, _value_msg = (
        "people header: {}, count: {}", "people list: {}, count: {}")
    people_scopes = self.core_elem.find_elements(
        *self._locators.PEOPLE_HEADERS_AND_VALUES_CSS)
    [selenium_utils.wait_until_stops_moving(people_scope)
     for people_scope in people_scopes]
    matched_people_scopes = [people_scope for people_scope in people_scopes
                             if header_text in people_scope.text]
    if len(matched_people_scopes) != 1:
      raise ValueError(
          messages.ExceptionsMessages.err_results_are_different.format(
              _header_msg.format(header_text, "1"),
              _value_msg.format(
                  [matched_people_scope.text
                   for matched_people_scope in matched_people_scopes],
                  len(matched_people_scopes))))
    people_scope = matched_people_scopes[0]
    _people_header = people_scope.find_element(
        *self._locators.PEOPLE_HEADER_CSS).text
    _people_value = people_scope.find_element(
        *self._locators.PEOPLE_VALUE_CSS).text
    # 'ASSIGNEE(S)\n(2)' to str 'ASSIGNEE(S)' and int '2'
    _people_header_parts = _people_header.splitlines()
    people_header_txt = _people_header_parts[0]
    people_count_from_header = (
        int(re.search(regex.TEXT_WO_PARENTHESES,
                      _people_header_parts[1]).group(1)))
    # filter: "\nuser@example.com\n(Inactive user)" to 'user@example.com'
    people_value_txt = [person for person in _people_value.splitlines()
                        if person != roles.NO_ROLE_UI]
    # if counters are same or None
    if not ((people_count_from_header == len(people_value_txt)) or
       (people_count_from_header == 0 and people_value_txt == ["None"])):
      raise ValueError(
          messages.ExceptionsMessages.err_counters_are_different.format(
              _header_msg.format(
                  _people_header_parts, str(people_count_from_header)),
              _value_msg.format(people_value_txt, len(people_value_txt))))
    return (people_header_txt,
            None if people_value_txt == ["None"] else people_value_txt)

  def get_headers_and_values_dict_from_cas_scopes(self, is_gcas_not_lcas=True):  # noqa: ignore=C901
    """Get text of all CAs headers and values elements scopes and convert it to
    dictionary. If 'is_gcas_not_lcas' then get GCAs, if not 'is_gcas_not_lcas'
    then get LCAs.
    Example:
    :return {'ca_header1': 'ca_value1', 'ca_header2': 'ca_value2', ...}
    """
    # pylint: disable=invalid-name
    # pylint: disable=too-many-branches
    selenium_utils.wait_for_js_to_load(self._driver)
    cas_locator = (self._locators.CAS_HEADERS_AND_VALUES if is_gcas_not_lcas
                   else self._locators.LCAS_HEADERS_AND_VALUES)
    cas_headers_and_values = self.info_widget_elem.find_elements(*cas_locator)
    dict_cas_scopes = {}
    if len(cas_headers_and_values) >= 1:
      list_text_cas_scopes = []
      for scope in cas_headers_and_values:
        ca_header_text = scope.text.splitlines()[0]
        if len(scope.text.splitlines()) >= 2:
          if scope.text.splitlines()[1].strip():
            list_text_cas_scopes.append(
                [ca_header_text, scope.text.splitlines()[1]])
          else:
            list_text_cas_scopes.append([ca_header_text, None])
        if len(scope.text.splitlines()) == 1:
          if (element.AdminWidgetCustomAttributes.CHECKBOX.upper() in
                  ca_header_text):
            list_text_cas_scopes.append(
                [ca_header_text,
                 unicode(int(base.Checkbox(self._driver, scope.find_element(
                     *self._locators.CAS_CHECKBOXES)).is_checked_via_js()))
                 ])
          else:
            list_text_cas_scopes.append([ca_header_text, None])
        if not is_gcas_not_lcas:
          self.collect_lcas_attr_name_value(
              ca_header_text, list_text_cas_scopes, scope)
      cas_headers, _cas_values = [list(text_cas_scope) for text_cas_scope
                                  in zip(*list_text_cas_scopes)]
      # conversion
      cas_values = []
      for ca_val in _cas_values:
        if ca_val is None:
          cas_values.append(None)
        elif ca_val == users.SUPERUSER_EMAIL:
          # Example User
          cas_values.append(
              unicode(objects.get_singular(objects.PEOPLE).title()))
        elif "/" in ca_val and len(ca_val) == 10:
          # Date
          _date = ca_val.split("/")
          cas_values.append(unicode("{y}-{m}-{d}".format(
              y=_date[2], m=_date[0], d=_date[1])))
        else:
          # Other
          cas_values.append(ca_val)
      dict_cas_scopes = dict(zip(cas_headers, cas_values))
    return dict_cas_scopes

  def collect_lcas_attr_name_value(self, ca_header_text, list_text_cas_scopes,
                                   scope):
    """Collect all local attribute with values"""
    ca_type = scope.get_attribute("class")
    if "custom-attribute-checkbox" in ca_type:
      ca_value = unicode(int(base.Checkbox(self._driver, scope.find_element(
          *self._locators.CAS_CHECKBOXES)).is_checked_via_js()))
    elif "custom-attribute-date" in ca_type:
      ca_value = scope.find_element(
          *locator.WidgetInfoPanel.
          DATE_CA_INPUT).get_attribute("value")
    elif "custom-attribute-text" in ca_type:
      ca_value = scope.find_element(
          *locator.WidgetInfoPanel.RICH_TEXT_CA_INPUT).text
    elif "custom-attribute-input" in ca_type:
      ca_value = scope.find_element(
          *locator.WidgetInfoPanel.TEXT_CA_INPUT).text
    elif "custom-attribute-dropdown" in ca_type:
      ca_value = (
          selenium_utils.get_element_value_js(
              self._driver, scope.find_element(
                  *locator.WidgetInfoPanel.DROPDOWN_CA_ITEM)))
    elif "custom-attribute-person" in ca_type:
      ca_value = scope.find_element(
          *locator.WidgetInfoPanel.PERSON_CA).text
    else:
      raise NotImplementedError()
    list_text_cas_scopes.append([ca_header_text, ca_value])

  def fill_lcas_attr_values(self):
    """Fill all local custom attribute with values."""
    selenium_utils.wait_for_js_to_load(self._driver)
    cas_headers_and_values = self.info_widget_elem.find_elements(
        *locator.WidgetInfoAssessment.LCAS_HEADERS_AND_VALUES)
    dict_cas_scopes = {}
    if len(cas_headers_and_values) >= 1:
      for scope in cas_headers_and_values:
        ca_type = scope.get_attribute("class")
        if "custom-attribute-date" in ca_type:
          ca_elem = base.DateCustomAttribute(
              scope, locator.WidgetInfoPanel.DATE_CA_FIELDS,
              locator.WidgetInfoPanel.DATE_CA_INPUT)
          ca_elem.set_value()
          dict_cas_scopes.update({scope.text: ca_elem.get_value()})

    selenium_utils.wait_for_element_text(
        self._driver,
        locator.WidgetInfoPanel.CA_SAVED_STATUS,
        element.GenericWidget.ALL_CHANGES_SAVED)
    return dict_cas_scopes

  def get_info_widget_obj_scope(self):
    """Get dict from object (text scope) which displayed on info page or
    info panel according to list of headers text and list of values text.
    """
    return dict(zip(self.list_all_headers_txt, self.list_all_values_txt))

  def _extend_list_all_scopes(self, headers, values):
    """Extend 'list all scopes' by headers' text and values' text."""
    self.list_all_headers_txt.extend(help_utils.convert_to_list(headers))
    self.list_all_values_txt.extend(help_utils.convert_to_list(values))

  def _extend_list_all_scopes_by_code(self):
    """Set attributes related to 'code' and extend 'list all scopes'
    accordingly.
    """
    self.code_lbl_txt, self.code_txt = (
        self.get_header_and_value_txt_from_custom_scopes(
            self._elements.CODE.upper()))
    self._extend_list_all_scopes(self.code_lbl_txt, self.code_txt)

  def _extend_list_all_scopes_by_cas(self):
    """Set attributes related to 'global custom attributes' and extend
    'list all scopes' accordingly.
    """
    self.cas_lbl_txt = self._elements.CAS.upper()
    self.cas_scope_txt = self.get_headers_and_values_dict_from_cas_scopes()
    self._extend_list_all_scopes(self.cas_lbl_txt, self.cas_scope_txt)

  def _extend_list_all_scopes_by_review_state(self):
    """Set attributes related to 'review state' and extend
    'list all scopes' accordingly.
    """
    # pylint: disable=invalid-name
    self.review_state_lbl = base.Label(
        self.info_widget_elem, self._locators.TXT_OBJECT_REVIEW)
    self.review_state_txt = self.get_review_state_txt()
    self._extend_list_all_scopes(
        self.review_state_lbl.text, self.review_state_txt)


class InfoPanel(object):
  """Class for Info Panels."""
  _locators = locator.WidgetInfoPanel

  def __init__(self, driver, info_widget_elem):
    self._driver = driver
    self.info_widget_elem = info_widget_elem

  def button_maximize_minimize(self):
    """Button (toggle) maximize and minimize for Info Panels."""
    return base.Toggle(
        self.info_widget_elem, self._locators.BUTTON_MAXIMIZE_MINIMIZE,
        locator.Common.NORMAL)

  def button_close(self):
    """Button close for Info Panels."""
    return self.info_widget_elem.find_element(*self._locators.BUTTON_CLOSE)


class SnapshotedInfoPanel(InfoPanel):
  """Class for Info Panels of shapshoted objects."""
  # pylint: disable=too-few-public-methods
  _locators = locator.WidgetSnapshotsInfoPanel
  dropdown_settings_cls = widget_info.Snapshots
  locator_link_get_latest_ver = _locators.LINK_GET_LAST_VER

  def snapshot_obj_version(self):
    """Label of snapshot version"""
    return base.Label(self.info_widget_elem, self._locators.SNAPSHOT_OBJ_VER)

  def open_link_get_latest_ver(self):
    """Click on link get latest version under Info panel."""
    base.Button(self.info_widget_elem,
                self.locator_link_get_latest_ver).click()
    return update_object.CompareUpdateObjectModal(self._driver)

  def is_link_get_latest_ver_exist(self):
    """Find link get latest version under Info panel.
    Return: True if link get latest version is exist,
            False if link get latest version is not exist.
    """
    return selenium_utils.is_element_exist(
        self.info_widget_elem, self.locator_link_get_latest_ver)


class Programs(WithObjectReview, InfoWidget):
  """Model for program object Info pages and Info panels."""
  # pylint: disable=too-many-instance-attributes
  _locators = locator.WidgetInfoProgram
  _elements = element.ProgramInfoWidget
  dropdown_settings_cls = widget_info.Programs

  def __init__(self, driver):
    super(Programs, self).__init__(driver)
    # todo: redesign 'Programs' cls init and related methods and tests
    self.show_advanced = base.Toggle(
        self.tab_container.active_tab_elem,
        self._locators.TOGGLE_SHOW_ADVANCED)
    self.show_advanced.toggle()
    self.description = base.Label(
        self.tab_container.active_tab_elem, self._locators.DESCRIPTION)
    self.description_entered = base.Label(
        self.tab_container.active_tab_elem, self._locators.DESCRIPTION_ENTERED)
    self.manager, self.manager_entered = (
        self.get_header_and_value_txt_from_people_scopes(
            self._elements.PROGRAM_MANAGERS.upper()))
    self._extend_list_all_scopes(
        self.manager, self.manager_entered)
    self.code = base.Label(
        self.tab_container.active_tab_elem, self._locators.CODE)
    self.code_entered = base.Label(
        self.tab_container.active_tab_elem, self._locators.CODE_ENTERED)
    self.effective_date = base.Label(
        self.tab_container.active_tab_elem, self._locators.EFFECTIVE_DATE)
    self.reference_urls = self.related_urls(self._reference_url_label)

  @property
  def effective_date_entered(self):
    return base.Label(
        self.tab_container.active_tab_elem,
        self._locators.EFFECTIVE_DATE_ENTERED)

  @property
  def notes_entered(self):
    return base.Label(self.info_widget_elem, self._locators.NOTES_ENTERED)

  def els_shown_for_editor(self):
    """Elements shown for user with edit permissions"""
    return [self.submit_for_review_link,
            self.info_3bbs_btn,
            self.comment_area.add_section,
            self.reference_urls.add_button] + list(self.inline_edit_controls)


class Workflows(InfoWidget):
  """Model for Workflow object Info pages and Info panels."""
  _locators = locator.WidgetInfoWorkflow

  def __init__(self, driver):
    super(Workflows, self).__init__(driver)

  def _extend_list_all_scopes_by_review_state(self):
    """Method overriding without action due to Workflows don't have
    'review states'.
    """
    pass


class Audits(WithAssignFolder, InfoWidget):
  """Model for Audit object Info pages and Info panels."""
  # pylint: disable=too-many-instance-attributes
  _locators = locator.WidgetInfoAudit
  _elements = element.AuditInfoWidget
  dropdown_settings_cls = widget_info.Audits

  def __init__(self, driver):
    super(Audits, self).__init__(driver)
    self.audit_captain_lbl_txt, self.audit_captain_txt = (
        self.get_header_and_value_txt_from_people_scopes(
            self._elements.AUDIT_CAPTAINS.upper()))
    self.auditor_lbl_txt, self.auditor_txt = (
        self.get_header_and_value_txt_from_people_scopes(
            self._elements.AUDITORS.upper()))
    self._extend_list_all_scopes(
        [self.audit_captain_lbl_txt, self.auditor_lbl_txt],
        [self.audit_captain_txt, self.auditor_txt])
    self.evidence_urls = self.related_urls(self._evidence_url_label)

  def _extend_list_all_scopes_by_review_state(self):
    """Method overriding without action due to Audits don't have
    'review states'.
    """
    pass

  def els_shown_for_editor(self):
    """Elements shown for user with edit permissions"""
    return [self.evidence_urls.add_button,
            self.assign_folder_button] + list(self.inline_edit_controls)


# Tab is opened when any action method is invoked:
# click(), text, present, etc.
#
# 1.
# page.assessment_tab.evidence_urls.add_button.click()
#
# 2.
# page.evidence_urls.add_button.click()
#
# self.evidence_urls = assessment_tab.evidence_urls()
# self.evidence_urls = self.evidence_urls(assessment_tab)
# self.evidence_urls = EvidenceUrls(assessment_tab)
#
# descendant_el.element1().element().parent().click()
#
# [x for x in descendant_el.element().elements()]

# class PageTab(object):
#   def __getattr__(self, attr):
#     if container_method:
#       pass  # invoke nerodia
#     else:
#       choose_tab()
#       invoke_attr()
#
#
# page_tab = PageTab()
# page_tab.element().elements()




class Assessments(InfoWidget):
  """Model for Assessment object Info pages and Info panels."""
  # pylint: disable=invalid-name
  # pylint: disable=too-many-instance-attributes
  _locators = locator.WidgetInfoAssessment
  _elements = element.AssessmentInfoWidget
  dropdown_settings_cls = widget_info.Assessments

  def __init__(self, driver):
    super(Assessments, self).__init__(driver)
    self.is_verified_lbl_txt = self._elements.VERIFIED.upper()
    self.is_verified = selenium_utils.is_element_exist(
        self.info_widget_elem, self._locators.ICON_VERIFIED)
    self.asmt_type_lbl_txt = self._elements.ASMT_TYPE.upper()
    self.asmt_type = base.Label(
        self.info_widget_elem, self._locators.ASMT_TYPE_CSS)
    self.asmt_type_txt = objects.get_obj_type(self.asmt_type.text)
    self.mapped_objects_lbl_txt = self._elements.MAPPED_OBJECTS.upper()
    self.mapped_objects_titles_txt = self._get_mapped_objs_titles_txt()
    self.lcas_scope_txt = self.get_headers_and_values_dict_from_cas_scopes(
        is_gcas_not_lcas=False)
    self.creators_lbl_txt, self.creators_txt = (
        self.get_header_and_value_txt_from_people_scopes(
            self._elements.CREATORS.upper()))
    self.assignees_lbl_txt, self.assignees_txt = (
        self.get_header_and_value_txt_from_people_scopes(
            self._elements.ASSIGNEES.upper()))
    self.verifiers_lbl_txt, self.verifiers_txt = (
        self.get_header_and_value_txt_from_people_scopes(
            self._elements.VERIFIERS.upper()))
    self.comments_panel = base.CommentsPanel(
        self.info_widget_elem, self._locators.COMMENTS_CSS)
    self.comments_lbl_txt = self.comments_panel.header_lbl.text
    self.comments_scopes_txt = self.comments_panel.scopes
    self._assessment_tab = self.page_tab("Assessment")
    self._other_attributes_tab = self.page_tab("Other Attributes")
    self.evidence_urls = self._assessment_tab.assessment_evidence_urls()
    self.primary_contacts = self._other_attributes_tab.related_people_list(
        "Primary Contacts")
    # todo: implement separate add lcas and gcas
    # todo: implement separate add mapped ctrls and mapped other objs
    self._extend_list_all_scopes(
        [self.is_verified_lbl_txt, self.creators_lbl_txt,
         self.assignees_lbl_txt, self.verifiers_lbl_txt,
         self.mapped_objects_lbl_txt, self.comments_lbl_txt,
         self.asmt_type_lbl_txt],
        [self.is_verified, self.creators_txt, self.assignees_txt,
         self.verifiers_txt, self.mapped_objects_titles_txt,
         self.comments_scopes_txt, self.asmt_type_txt])

  def _get_mapped_objs_titles_txt(self):
    """Return lists of str for mapped snapshots titles text from current tab.
    """
    mapped_items = self.tab_container.active_tab_elem.find_elements(
        *self._locators.MAPPED_SNAPSHOTS_CSS)
    return [mapped_el.find_element(
            *self._locators.MAPPED_SNAPSHOT_TITLE_CSS).text
            for mapped_el in mapped_items]

  def get_info_widget_obj_scope(self):
    """Get an Assessment object's text scope (headers' (real and synthetic)
    and values' txt) from Info Widget navigating through the Assessment's tabs.
    """
    self.tab_container.tab_controller.active_tab = (
        element.AssessmentTabContainer.OTHER_ATTRS_TAB)
    self.core_elem = self.tab_container.active_tab_elem
    self.mapped_objects_titles_txt += self._get_mapped_objs_titles_txt()
    self._extend_list_all_scopes_by_code()
    self._extend_list_all_scopes_by_cas()
    obj_scope = {
      "evidence_urls": self.evidence_urls.get_urls(),
      "primary_contacts": self.primary_contacts.get_people_emails()
    }
    obj_scope.update(zip(self.list_all_headers_txt, self.list_all_values_txt))
    return obj_scope

  def _extend_list_all_scopes_by_cas(self):
    """Extend attributes related to 'local and global custom attributes' and
    extend 'list all scopes' if 'Other Attributes' tab opened.
    """
    # todo: implement separate entities' model for lcas and gcas
    if (self.tab_container.tab_controller.active_tab.text ==
            element.AssessmentTabContainer.OTHER_ATTRS_TAB):
      self.cas_lbl_txt = self._elements.CAS.upper()
      self.cas_scope_txt = self.get_headers_and_values_dict_from_cas_scopes()
      self.cas_scope_txt.update(self.lcas_scope_txt)
      self._extend_list_all_scopes(self.cas_lbl_txt, self.cas_scope_txt)

  def _extend_list_all_scopes_by_review_state(self):
    """Method overriding without action due to Assessments don't have
    'review states'.
    """
    pass

  def click_complete(self):
    """Click on 'Complete' button."""
    base.Button(self.info_widget_elem,
                WidgetInfoAssessment.BUTTON_COMPLETE).click()

  def click_verify(self):
    """Click on 'Verify' button."""
    base.Button(self.info_widget_elem,
                WidgetInfoAssessment.BUTTON_VERIFY).click()

  def click_needs_rework(self):
    """Click on 'Needs Rework' button."""
    base.Button(self.info_widget_elem,
                WidgetInfoAssessment.BUTTON_NEEDS_REWORK).click()

  def choose_and_fill_dropdown_lca(self, dropdown_id, option_title, **kwargs):
    """Choose and fill comment or url for Assessment dropdown."""
    self.select_ca_dropdown_option(dropdown_id, option_title)
    SetValueForAsmtDropdown(self._driver).fill_dropdown_lca(**kwargs)
    selenium_utils.get_when_clickable(
        self._driver, WidgetInfoAssessment.BUTTON_COMPLETE)

  def select_ca_dropdown_option(self, dropdown_id, option_value):
    """Select custom attribute dropdown option."""
    dropdown_locator = (
        By.CSS_SELECTOR, "#form-field-{}".format(dropdown_id))
    selenium_utils.get_when_clickable(
        self.info_widget_elem, dropdown_locator)
    base.DropdownStatic(self.info_widget_elem,
                        dropdown_locator).select(option_value)

  def edit_answers(self):
    """Click to Edit Answers and Confirm"""
    self._browser.button(text="Edit Answers").click()
    self._browser.element(class_name="modal").link(text="Confirm").click()
    self.wait_save()


class AssessmentTemplates(InfoWidget):
  """Model for Assessment Template object Info pages and Info panels."""
  _locators = locator.WidgetInfoAssessmentTemplate

  def __init__(self, driver):
    super(AssessmentTemplates, self).__init__(driver)

  def _extend_list_all_scopes_by_code(self):
    """Method overriding without action due to Assessment Templates don't have
    'code'.
    """
    pass

  def _extend_list_all_scopes_by_cas(self):
    """Method overriding without action due to Assessment Templates don't have
    'global custom attributes'.
    """
    pass

  def _extend_list_all_scopes_by_review_state(self):
    """Method overriding without action due to Assessment Templates don't have
    'review states'.
    """
    pass


class Issues(InfoWidget):
  """Model for Issue object Info pages and Info panels."""
  _locators = locator.WidgetInfoIssue
  _elements = element.IssueInfoWidget

  def __init__(self, driver):
    super(Issues, self).__init__(driver)


class Regulations(InfoWidget):
  """Model for Assessment object Info pages and Info panels."""
  _locators = locator.WidgetInfoRegulations

  def __init__(self, driver):
    super(Regulations, self).__init__(driver)


class Policies(InfoWidget):
  """Model for Policy object Info pages and Info panels."""
  _locators = locator.WidgetInfoPolicy

  def __init__(self, driver):
    super(Policies, self).__init__(driver)


class Standards(InfoWidget):
  """Model for Standard object Info pages and Info panels."""
  _locators = locator.WidgetInfoStandard

  def __init__(self, driver):
    super(Standards, self).__init__(driver)


class Contracts(InfoWidget):
  """Model for Contract object Info pages and Info panels."""
  _locators = locator.WidgetInfoContract

  def __init__(self, driver):
    super(Contracts, self).__init__(driver)


class Clauses(InfoWidget):
  """Model for Clause object Info pages and Info panels."""
  _locators = locator.WidgetInfoClause

  def __init__(self, driver):
    super(Clauses, self).__init__(driver)


class Requirements(InfoWidget):
  """Model for Requirement object Info pages and Info panels."""
  _locators = locator.WidgetInfoRequirement

  def __init__(self, driver):
    super(Requirements, self).__init__(driver)


class Controls(WithAssignFolder, WithObjectReview, InfoWidget):
  """Model for Control object Info pages and Info panels."""
  # pylint: disable=too-many-instance-attributes
  _locators = locator.WidgetInfoControl
  _elements = element.ControlInfoWidget
  dropdown_settings_cls = widget_info.Controls

  def __init__(self, driver):
    super(Controls, self).__init__(driver)
    self.admin_text, self.admin_entered_text = (
        self.get_header_and_value_txt_from_people_scopes(
            self._elements.ADMIN.upper()))
    self.primary_contact_text, self.primary_contact_entered_text = (
        self.get_header_and_value_txt_from_people_scopes(
            self._elements.PRIMARY_CONTACTS.upper()))
    self.reference_urls = self.related_urls(self._reference_url_label)
    self._extend_list_all_scopes(
        [self.admin_text, self.primary_contact_text],
        [self.admin_entered_text, self.primary_contact_entered_text])
    self._add_obj_review_to_lsopes()

  def _add_obj_review_to_lsopes(self):
    """Extend list of scopes by object review section """
    review_msg = None
    if selenium_utils.is_element_exist(self._driver,
                                       self._locators.REVIEW_REJECTED_TXT):
      review_msg = self._driver.find_element(*self._locators.
                                             REVIEW_REJECTED_TXT).text
    elif selenium_utils.is_element_exist(self._driver,
                                         self._locators.REVIEW_APPROVED_TXT):
      review_msg = self._driver.find_element(*self._locators.
                                             REVIEW_APPROVED_TXT).text

    self._extend_list_all_scopes(self._elements.OBJECT_REVIEW_FULL,
                                 review_msg)

  def open_submit_for_review_popup(self):
    """Open submit for control popub by clicking on corresponding button."""
    self._driver.find_element(
        *WidgetInfoControl.LINK_SUBMIT_FOR_REVIEW).click()
    selenium_utils.wait_for_js_to_load(self._driver)

  def select_assignee_user(self, user_email):
    """Select assignee user from dropdown on submit for review popup."""
    elem = self._driver.find_element(*WidgetInfoControl.ASSIGN_REVIEWER_EMPTY)
    elem.send_keys(user_email)
    selenium_utils.wait_for_js_to_load(self._driver)
    selenium_utils.get_when_all_visible(self._driver, WidgetInfoControl.
                                        ASSIGN_REVIEWER_DROPDOWN)
    base.ElementsList(
        self._driver,
        self._driver.find_element(*WidgetInfoControl.
                                  ASSIGN_REVIEWER_DROPDOWN)).get_item(
        user_email).click()

  def select_first_available_date(self):
    """Select first available day on datepicker on submit for review popup."""
    date_picker = base.DatePicker(self._driver,
                                  WidgetInfoControl.DATE_PICKER_FIELD,
                                  WidgetInfoControl.DATE_PICKER_LOCATOR)
    date_picker.select_month_start()

  def click_submit(self):
    """Click submit."""
    self._driver.find_element(*WidgetInfoControl.SUBMIT_REVIEW_BUTTON).click()
    selenium_utils.wait_for_js_to_load(self._driver)

  def click_approve_review(self):
    """Click approve review button."""
    self._driver.find_element(*WidgetInfoControl.
                              OBJECT_REVIEW_APPROVE_BTN).click()

  def click_decline_review(self):
    """Click on becline review button."""
    self._driver.find_element(*WidgetInfoControl.
                              OBJECT_REVIEW_DECLINE_BTN).click()

  def leave_decline_comment(self, comment_msg):
    """Leave decline comment for decline option."""
    comments_elem = self._driver.find_element(*WidgetInfoControl.
                                              DECLINE_REVIEW_COMMENTS)
    comments_elem.click()
    comments_elem.send_keys(comment_msg)

  def click_save_and_close_on_decline(self):
    """Click save and close on decline popup."""
    self._driver.find_element(
        *WidgetInfoControl.SAVE_AND_CLOSE_BTN).click()

  def els_shown_for_editor(self):
    """Elements shown for user with edit permissions"""
    return [self.submit_for_review_link,
            self.info_3bbs_btn,
            self.comment_area.add_section,
            self.reference_urls.add_button,
            self.assign_folder_button] + list(self.inline_edit_controls)


class Objectives(InfoWidget):
  """Model for Objective object Info pages and Info panels."""
  _locators = locator.WidgetInfoObjective

  def __init__(self, driver):
    super(Objectives, self).__init__(driver)


class OrgGroups(InfoWidget):
  """Model for Org Group object Info pages and Info panels."""
  _locators = locator.WidgetInfoOrgGroup
  dropdown_settings_cls = widget_info.OrgGroups

  def __init__(self, driver):
    super(OrgGroups, self).__init__(driver)


class Vendors(InfoWidget):
  """Model for Vendor object Info pages and Info panels."""
  _locators = locator.WidgetInfoVendor

  def __init__(self, driver):
    super(Vendors, self).__init__(driver)


class AccessGroup(InfoWidget):
  """Model for Access Group object Info pages and Info panels."""
  _locators = locator.WidgetInfoAccessGroup

  def __init__(self, driver):
    super(AccessGroup, self).__init__(driver)


class Systems(InfoWidget):
  """Model for System object Info pages and Info panels."""
  _locators = locator.WidgetInfoSystem
  dropdown_settings_cls = widget_info.Systems

  def __init__(self, driver):
    super(Systems, self).__init__(driver)


class Processes(InfoWidget):
  """Model for Process object Info pages and Info panels."""
  _locators = locator.WidgetInfoProcess
  dropdown_settings_cls = widget_info.Processes

  def __init__(self, driver):
    super(Processes, self).__init__(driver)


class DataAssets(InfoWidget):
  """Model for Data Asset object Info pages and Info panels."""
  _locators = locator.WidgetInfoDataAsset
  dropdown_settings_cls = widget_info.DataAssets

  def __init__(self, driver):
    super(DataAssets, self).__init__(driver)


class Products(InfoWidget):
  """Model for Product object Info pages and Info panels."""
  _locators = locator.WidgetInfoProduct
  dropdown_settings_cls = widget_info.Products

  def __init__(self, driver):
    super(Products, self).__init__(driver)


class Projects(InfoWidget):
  """Model for Project object Info pages and Info panels."""
  _locators = locator.WidgetInfoProject
  dropdown_settings_cls = widget_info.Projects

  def __init__(self, driver):
    super(Projects, self).__init__(driver)


class Facilities(InfoWidget):
  """Model for Facility object Info pages and Info panels."""
  _locators = locator.WidgetInfoFacility

  def __init__(self, driver):
    super(Facilities, self).__init__(driver)


class Markets(InfoWidget):
  """Model for Market object Info pages and Info panels."""
  _locators = locator.WidgetInfoMarket

  def __init__(self, driver):
    super(Markets, self).__init__(driver)


class Risks(InfoWidget):
  """Model for Risk object Info pages and Info panels."""
  _locators = locator.WidgetInfoRisk

  def __init__(self, driver):
    super(Risks, self).__init__(driver)


class Threats(InfoWidget):
  """Model for Threat object Info pages and Info panels."""
  _locators = locator.WidgetInfoThreat

  def __init__(self, driver):
    super(Threats, self).__init__(driver)


class People(base.Widget):
  """Model for People object Info pages and Info panels."""
  # pylint: disable=too-few-public-methods
  _locators = locator.WidgetInfoPeople


class Dashboard(base.Widget):
  """Model for Dashboard object Info pages and Info panels."""
  _locators = locator.Dashboard

  def __init__(self, driver):
    super(Dashboard, self).__init__(driver)
    self.start_new_program_btn = base.Button(
        self._driver, self._locators.START_NEW_PROGRAM_BTN_CSS)
    self.start_new_audit_btn = base.Button(
        self._driver, self._locators.START_NEW_AUDIT_BTN_CSS)
    self.start_new_workflow_btn = base.Button(
        self._driver, self._locators.START_NEW_WORKFLOW_BTN_CSS)
    self.create_task_btn = base.Button(
        self._driver, self._locators.CREATE_TASK_BTN_CSS)
    self.create_object_btn = base.Button(
        self._driver, self._locators.CREATE_OBJECT_BTN_CSS)
    self.all_objects_btn = base.Button(
        self._driver, self._locators.ALL_OBJECTS_BTN_CSS)
