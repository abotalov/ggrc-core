# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Assessments Workflow smoke tests."""
# pylint: disable=no-self-use
# pylint: disable=invalid-name
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=redefined-outer-name
import random

import pytest

from lib import base, factory, users
from lib.constants import (
    messages, element, value_aliases as alias, objects, object_states, roles)
from lib.constants.element import AdminWidgetCustomAttributes
from lib.entities import entities_factory
from lib.entities.entities_factory import (
    CustomAttributeDefinitionsFactory, PeopleFactory)
from lib.entities.entity import Representation
from lib.service import rest_facade, rest_service, webui_service
from lib.utils import string_utils
from lib.utils.filter_utils import FilterUtils
from lib.utils.string_utils import StringMethods


def _create_mapped_asmt(audit, assessment_type, objs_to_map):
  """Create assessment with assessment type=`assessment_type` and
  map it to snapshots of `objs_to_map`"""
  assessment = rest_facade.create_asmt(
      audit, assessment_type=assessment_type)
  for obj in objs_to_map:
    rest_facade.map_to_snapshot(assessment, obj=obj, parent_obj=audit)
  assessment.update_attrs(mapped_objects=objs_to_map)
  return assessment


def _create_asmt_template(audit, assessment_type, cads):
  """Create assessment with assessment type=`assessment_type` and
  map it to snapshots of `objs_to_map`"""
  cads_rest = cads if cads else (
      CustomAttributeDefinitionsFactory.generate_cads_for_asmt_tmpls(cads))
  assessment_template = rest_facade.create_asmt_template(
      audit, assessment_type=assessment_type,
      custom_attribute_definitions=cads_rest)
  return assessment_template


def _assert_asmt(asmts_ui_service, exp_asmt, is_cas_check_required=False):
  """Assert that assessment `exp_asmt` on UI is the same as in
  `exp_asmt`."""
  # "audit" not shown in UI
  # "custom_attributes" not returned on POST /api/assessments
  actual_asmt = asmts_ui_service.get_obj_from_info_page(exp_asmt)
  if is_cas_check_required:
    base.Test().general_contain_assert(exp_asmt.repr_ui(),
                                       actual_asmt, "audit")
  else:
    base.Test().general_equal_assert(exp_asmt.repr_ui(),
                                     actual_asmt, "audit", "custom_attributes")


class TestAssessmentsWorkflow(base.Test):
  """Tests for Assessments Workflow functionality."""
  info_service = rest_service.ObjectsInfoService

  @pytest.mark.smoke_tests
  def test_add_comment_to_asmt_via_info_panel(
      self, program, audit, assessment, selenium
  ):
    """Check via UI of possibility to correctly add comment to Assessment via
    Info Panel.
    Preconditions:
    - Program created via REST API.
    - Audit created under Program via REST API.
    - Assessment created under Audit via REST API.
    Test parameters: None
    """
    expected_asmt_comments = [entities_factory.CommentsFactory().create()]
    expected_asmt = assessment
    asmts_ui_service = webui_service.AssessmentsService(selenium)
    asmt_comments_panel = asmts_ui_service.add_comments(
        src_obj=audit, obj=expected_asmt,
        comment_objs=expected_asmt_comments)
    assert asmt_comments_panel.is_input_empty is True
    # 'expected_asmt_comments': created_at (None) *factory
    expected_asmt_comments = [expected_comment.update_attrs(
        created_at=self.info_service().get_comment_obj(
            paren_obj=expected_asmt,
            comment_description=expected_comment.description).created_at
    ).repr_ui() for expected_comment in expected_asmt_comments]
    # 'expected_asmt': updated_at (outdated)
    expected_asmt.update_attrs(
        updated_at=self.info_service().get_obj(obj=expected_asmt).updated_at,
        comments=expected_asmt_comments,
        status=object_states.IN_PROGRESS).repr_ui()
    actual_asmt = asmts_ui_service.get_obj_from_info_page(obj=expected_asmt)
    # 'actual_asmt': audit (None)
    self.general_equal_assert(expected_asmt, actual_asmt, "audit", "comments")
    self.xfail_equal_assert(
        expected_asmt, actual_asmt, "Issue in app GGRC-3094", "comments")

  @pytest.mark.smoke_tests
  def test_asmt_logs(
      self, new_program_rest, new_audit_rest, new_assessment_rest, selenium
  ):
    """Test for validation of Assessment log pane.
    Acceptance criteria:
      1) 3 log items at the log pane
      2) all items return 'True' for all attrs.
    """
    log_items_validation = webui_service.AssessmentsService(
        selenium).get_log_pane_validation_result(obj=new_assessment_rest)
    log_validation_results = [all(item_result.values()) for item_result in
                              log_items_validation]
    assert ([True] * 2) == log_validation_results, str(log_items_validation)

  @pytest.mark.smoke_tests
  def test_raise_issue(
      self, new_program_rest, new_audit_rest, new_assessment_rest, selenium
  ):
    """Test for checking raising Issues in Related Issues Tab. Open
    Related Issues tab on Assessments Info page. Raise Issue with pre-defined
    attributes via "raise issue" button. Compare expected Issue title and
    actual issue_titles.
    """
    expected_issue = (entities_factory.IssuesFactory().create().repr_ui())
    asmts_ui_service = webui_service.AssessmentsService(selenium)
    asmts_ui_service.raise_issue(new_assessment_rest, expected_issue)
    related_issues_titles = asmts_ui_service.get_related_issues_titles(
        obj=new_assessment_rest)
    assert related_issues_titles == [expected_issue.title]

  @pytest.mark.smoke_tests
  @pytest.mark.parametrize(
      ("dynamic_objects_w_factory_params",
       "action", "expected_final_state"),
      [(("new_assessment_rest", {"status": object_states.NOT_STARTED}),
        "edit_obj_via_edit_modal_from_info_page",
        object_states.NOT_STARTED),
       (("new_assessment_rest", {"status": object_states.NOT_STARTED,
                                 "verifiers": [PeopleFactory.superuser]}),
        "edit_obj_via_edit_modal_from_info_page",
        object_states.NOT_STARTED),
       (("new_assessment_rest", {"status": object_states.IN_PROGRESS}),
        "edit_obj_via_edit_modal_from_info_page",
        object_states.IN_PROGRESS),
       (("new_assessment_rest", {"status": object_states.IN_PROGRESS,
                                 "verifiers": [PeopleFactory.superuser]}),
        "edit_obj_via_edit_modal_from_info_page",
        object_states.IN_PROGRESS),
       (("new_assessment_rest", {"status": object_states.COMPLETED}),
        "edit_obj_via_edit_modal_from_info_page",
        object_states.IN_PROGRESS),
       (("new_assessment_rest", {"status": object_states.COMPLETED,
                                 "verifiers": [PeopleFactory.superuser]}),
        "edit_obj_via_edit_modal_from_info_page",
        object_states.IN_PROGRESS),
       (("new_assessment_rest", {"status": object_states.NOT_STARTED}),
        "complete_assessment",
        object_states.COMPLETED),
       (("new_assessment_rest", {"status": object_states.NOT_STARTED,
                                 "verifiers": [PeopleFactory.superuser]}),
        "complete_assessment",
        object_states.READY_FOR_REVIEW),
       (("new_assessment_rest", {"status": object_states.IN_PROGRESS}),
        "complete_assessment",
        object_states.COMPLETED),
       (("new_assessment_rest", {"status": object_states.IN_PROGRESS,
                                 "verifiers": [PeopleFactory.superuser]}),
        "complete_assessment",
        object_states.READY_FOR_REVIEW)],
      ids=["Edit asmt's title w'o verifier 'Not Started' - 'Not Started'",
           "Edit asmt's title w' verifier 'Not Started' - 'Not Started'",
           "Edit asmt's title w'o verifier 'In Progress' - 'In Progress'",
           "Edit asmt's title w' verifier 'In Progress' - 'In Progress'",
           "Edit asmt's title w'o verifier 'Completed' - 'In Progress'",
           "Edit asmt's title w' verifier 'Completed' - 'In Progress'",
           "Complete asmt w'o verifier 'Not Started' - 'Completed'",
           "Complete asmt w' verifier 'Not Started' - 'In Review'",
           "Complete asmt w'o verifier 'In Progress' - 'Completed'",
           "Complete asmt w' verifier 'In Progress' - 'In Review'"],
      indirect=["dynamic_objects_w_factory_params"])
  def test_check_asmt_state_change(
      self, new_program_rest, new_audit_rest, dynamic_objects_w_factory_params,
      action, expected_final_state, selenium
  ):
    """Check Assessment workflow status change to correct state.
    Preconditions:
    - Program created via REST API.
    - Audit created under Program via REST API.
    - Assessment created and updated under Audit via REST API.
    """
    expected_asmt = dynamic_objects_w_factory_params
    asmts_ui_service = webui_service.AssessmentsService(selenium)
    getattr(asmts_ui_service, action)(expected_asmt)
    # 'expected_asmt': updated_at (outdated)
    expected_asmt.update_attrs(
        title=(element.AssessmentInfoWidget.TITLE_EDITED_PART +
               expected_asmt.title if "edit" in action
               else expected_asmt.title),
        status=expected_final_state.title(),
        updated_at=self.info_service().get_obj(
            obj=expected_asmt).updated_at).repr_ui()
    actual_asmt = asmts_ui_service.get_obj_from_info_page(expected_asmt)
    # 'actual_asmt': audit (None)
    self.general_equal_assert(expected_asmt, actual_asmt, "audit")

  @pytest.mark.smoke_tests
  @pytest.mark.parametrize(
      "initial_state, action, end_state",
      [
          (object_states.READY_FOR_REVIEW, "verify_assessment",
           object_states.COMPLETED),
          (object_states.NOT_STARTED, "deprecate_assessment",
           object_states.DEPRECATED),
          (object_states.READY_FOR_REVIEW, "reject_assessment",
           object_states.REWORK_NEEDED),
          (object_states.COMPLETED, "edit_assessment_answers",
           object_states.IN_PROGRESS)
      ]
  )
  def test_change_asmt_state_as_verifier(
      self, program, audit, initial_state, action, end_state, selenium
  ):
    """Tests for changing assessment state as assessment verifier"""
    verifier = rest_facade.create_user_with_role(roles.CREATOR)
    asmt = rest_facade.create_asmt(audit,
                                   status=initial_state, verifiers=[verifier])
    users.set_current_user(verifier)
    asmt_service = webui_service.AssessmentsService(selenium)
    getattr(asmt_service, action)(asmt)
    actual_asmt = asmt_service.get_obj_from_info_page(asmt)
    asmt.update_attrs(
        updated_at=rest_facade.get_obj(asmt).updated_at,
        status=end_state,
        verified=(True if action == "verify_assessment" else False)).repr_ui()
    self.general_equal_assert(asmt, actual_asmt, "audit")

  @pytest.mark.smoke_tests
  @pytest.mark.parametrize("operator", [alias.EQUAL_OP, alias.CONTAINS_OP])
  def test_destructive_asmts_gcas_filtering(
      self, new_program_rest, new_audit_rest, gcads_for_asmt,
      new_assessments_rest, operator, selenium
  ):
    """Test for checking filtering of Assessment by Global Custom Attributes
    in audit scope.
    Preconditions:
    - Program created via REST API.
    - Audit created via REST API.
    - Global Custom Attributes for Assessment created via REST API.
    - Assessments created via REST API.
    """
    unchecked_asmt = new_assessments_rest[0]
    checked_asmt = new_assessments_rest[1]

    checkbox_value = random.choice([True, False])
    print "Checkbox value: {}".format(checkbox_value)
    self._set_values_for_assessment(
        unchecked_asmt, gcads_for_asmt,
        only_checkbox=True, checkbox_value=checkbox_value)
    cavs = self._set_values_for_assessment(
        checked_asmt, gcads_for_asmt,
        only_checkbox=False, checkbox_value=not checkbox_value)

    self._check_assessments_filtration(checked_asmt, cavs,
                                       operator, new_audit_rest, selenium)

  @pytest.mark.smoke_tests
  @pytest.mark.parametrize("operator", [alias.EQUAL_OP])
  def test_destructive_asmts_lcas_filtering(
      self, new_program_rest, new_controls_rest,
      map_new_program_rest_to_new_controls_rest,
      new_audit_rest,
      new_assessment_template_with_cas_rest,
      new_assessments_from_template_rest,
      operator, selenium
  ):
    """Test for checking filtering of Assessment by Local Custom Attributes
    in audit scope.
    Preconditions:
    - Program created via REST API.
    - Controls created via REST API and mapped to program.
    - Audit created via REST API.
    - Assessment template with LCA created via REST API.
    - Assessments for assessment template created via REST API.
    """
    def set_values_for_assessment(assessment, only_checkbox, checkbox_value):
      """Set LCA values for assessment"""
      cads = [
          CustomAttributeDefinitionsFactory().create(**definition)
          for definition
          in assessment.cads_from_template()]
      return self._set_values_for_assessment(
          assessment, cads, only_checkbox, checkbox_value)

    unchecked_asmt = new_assessments_from_template_rest[0]
    checked_asmt = new_assessments_from_template_rest[1]

    checkbox_value = random.choice([True, False])
    print "Checkbox value: {}".format(checkbox_value)
    set_values_for_assessment(
        unchecked_asmt, only_checkbox=True, checkbox_value=checkbox_value)
    set_attr_values = set_values_for_assessment(
        checked_asmt, only_checkbox=False, checkbox_value=not checkbox_value)

    self._check_assessments_filtration(checked_asmt,
                                       set_attr_values,
                                       operator, new_audit_rest, selenium)

  @staticmethod
  def _set_values_for_assessment(assessment, cads,
                                 only_checkbox, checkbox_value):
    """Set CA values for assessment"""
    checkbox_cad = Representation.filter_objs_by_attrs(
        objs=cads,
        attribute_type=element.AdminWidgetCustomAttributes.CHECKBOX)
    if only_checkbox:
      cavs = [CustomAttributeDefinitionsFactory.generate_cav(
          checkbox_cad, checkbox_value)]
    else:
      cavs = CustomAttributeDefinitionsFactory.generate_cavs(cads)
      for cav in cavs:
        if cav.custom_attribute_id == checkbox_cad.id:
          cav.attribute_value = checkbox_value
    rest_service.AssessmentsService().update_obj(
        obj=assessment,
        custom_attribute_values=[cav.__dict__ for cav in cavs])
    return cavs

  @staticmethod
  def _check_assessments_filtration(assessment, cavs, operator,
                                    audit, selenium):
    """Check that filtration of assessments works."""
    # pylint: disable=too-many-locals
    cads = [Representation.repr_dict_to_obj(cad)
            for cad in assessment.custom_attribute_definitions]
    filter_exprs = FilterUtils().get_filter_exprs_by_cavs(
        cads, cavs, operator)
    assessment = Representation.extract_objs_wo_excluded_attrs(
        [assessment.repr_ui()],
        *(Representation.tree_view_attrs_to_exclude + (
            "audit", "assessment_type", "modified_by"))
    )[0]
    expected_results = [{"filter": filter_expr, "objs": [assessment]}
                        for filter_expr in filter_exprs]
    actual_results = []
    for filter_expr in filter_exprs:
      result = {
          "filter": filter_expr,
          "objs": webui_service.AssessmentsService(
              selenium).filter_and_get_list_objs_from_tree_view(audit,
                                                                filter_expr)
      }
      actual_results.append(result)
    error_message = messages.AssertionMessages.format_err_msg_equal(
        [{exp_res["filter"]: [exp_obj.title for exp_obj in exp_res["objs"]]}
         for exp_res in expected_results],
        [{act_res["filter"]: [act_obj.title for act_obj in act_res["objs"]]}
         for act_res in actual_results]
    ) + messages.AssertionMessages.format_err_msg_equal(
        StringMethods.convert_list_elements_to_list(
            [exp_res["objs"] for exp_res in expected_results]),
        StringMethods.convert_list_elements_to_list(
            [act_res["objs"] for act_res in actual_results]))
    assert expected_results == actual_results, error_message

  @pytest.mark.smoke_tests
  @pytest.mark.parametrize(
      "dynamic_objects, dynamic_relationships",
      [("new_objective_rest", "map_new_program_rest_to_new_objective_rest"),
       ("new_control_rest", "map_new_program_rest_to_new_control_rest")],
      indirect=True)
  def test_map_snapsots_to_asmt_via_edit_modal(
      self, new_program_rest, dynamic_objects, dynamic_relationships,
      new_audit_rest, new_assessment_rest, selenium
  ):
    """Check Assessment can be mapped with snapshot via Modal Edit
    on Assessments Info Page. Additional check existing of mapped obj Titles
    on Modal Edit.
    Preconditions:
    - Program, dynamic_objects created via REST API.
    - dynamic_objects mapped to Program via REST API.
    - Audit created under Program via REST API.
    - Assessment created under audit via REST API.
    Test parameters:
    - 'dynamic_objects'.
    - 'dynamic_relationships'.
    """
    expected_asmt = (new_assessment_rest.update_attrs(
        mapped_objects=[dynamic_objects]))
    expected_titles = [dynamic_objects.title]
    asmts_ui_service = webui_service.AssessmentsService(selenium)
    actual_titles = (
        asmts_ui_service.map_objs_and_get_mapped_titles_from_edit_modal(
            expected_asmt, expected_asmt.mapped_objects))
    assert expected_titles == actual_titles
    # 'expected_asmt': updated_at (outdated)
    expected_asmt.update_attrs(updated_at=self.info_service().get_obj(
        obj=expected_asmt).updated_at).repr_ui()
    actual_asmt = asmts_ui_service.get_obj_from_info_page(expected_asmt)
    # 'actual_asmts': audit (None)
    self.general_equal_assert(expected_asmt, actual_asmt, "audit")

  @pytest.mark.smoke_tests
  def test_asmt_from_template_w_dropdown_url(self, program,
                                             control_mapped_to_program, audit,
                                             selenium):
    """Check evidence url could be filled in
    via Assessment dropdown.
    Objects structure:
    Program.
    -> Control mapped to program.
    -> Audit.
      -> Asmt template with evidence url dropdown.
        -> Autogenerated asmt.
    """
    url = StringMethods.random_string()
    asmt_template_w_dropdown = rest_facade.create_asmt_template(
        audit, cad_type=AdminWidgetCustomAttributes.DROPDOWN,
        dropdown_types_list=["url"])
    expected_asmt = rest_facade.create_asmt_from_template(
        audit, asmt_template_w_dropdown, control_mapped_to_program)
    dropdown = CustomAttributeDefinitionsFactory().create(
        **expected_asmt.cads_from_template()[0])
    asmt_service = webui_service.AssessmentsService(selenium)
    expected_asmt = asmt_service.choose_and_fill_dropdown_lca(
        expected_asmt, dropdown, url=url)
    expected_asmt.update_attrs(updated_at=self.info_service().get_obj(
        obj=expected_asmt).updated_at, evidence_urls=[url],
        mapped_objects=[control_mapped_to_program.title],
        status=object_states.IN_PROGRESS).repr_ui()
    actual_asmt = asmt_service.get_obj_from_info_page(obj=expected_asmt)
    self.general_equal_assert(expected_asmt, actual_asmt, "audit")

  @pytest.mark.smoke_tests
  def test_asmt_from_template_w_dropdown_comment(self, program,
                                                 control_mapped_to_program,
                                                 audit, selenium):
    """Check evidence comment could be filled in
    via Assessment dropdown.
    Objects structure:
    Program.
    -> Control mapped to program.
    -> Audit.
      -> Asmt template with evidence comment dropdown.
        -> Autogenerated asmt.
    """
    comment_text = entities_factory.CommentsFactory().create().description
    asmt_template_w_dropdown = rest_facade.create_asmt_template(
        audit, cad_type=AdminWidgetCustomAttributes.DROPDOWN,
        dropdown_types_list=["comment"])
    expected_asmt = rest_facade.create_asmt_from_template(
        audit, asmt_template_w_dropdown, control_mapped_to_program)
    dropdown = CustomAttributeDefinitionsFactory().create(
        **expected_asmt.cads_from_template()[0])
    asmt_service = webui_service.AssessmentsService(selenium)
    expected_asmt = asmt_service.choose_and_fill_dropdown_lca(
        expected_asmt, dropdown, comment=comment_text)
    expected_asmt.update_attrs(
        updated_at=self.info_service().get_obj(obj=expected_asmt).updated_at,
        mapped_objects=[control_mapped_to_program.title],
        status=object_states.IN_PROGRESS).repr_ui()
    actual_asmt = asmt_service.get_obj_from_info_page(obj=expected_asmt)
    actual_comment_texts = [
        comment["description"] for comment in actual_asmt.comments]
    self.general_equal_assert(expected_asmt, actual_asmt, "audit", "comments")
    assert actual_comment_texts == [comment_text]

  @pytest.mark.smoke_tests
  @pytest.mark.parametrize("attr_type",
                           AdminWidgetCustomAttributes.ALL_CA_TYPES)
  def test_asmt_from_template_lcas(self, control_mapped_to_program, audit,
                                   attr_type, selenium):
    """
    1. Create a program via REST
    2. Create a control within a program via REST
    3. Create an audit within a program via REST
    4. Create an assessment template with each type of
     local custom attribute within audit via REST
    5. Generate an assessment from assessment template and control
     snapshot via REST
    6. Open this assessment in UI
    7. Fill local custom attribute
    8. Reload page and check that object built from the page looks as expected
    """
    cad = CustomAttributeDefinitionsFactory().create(
        is_add_rest_attrs=True, attribute_type=attr_type)
    cavs = (CustomAttributeDefinitionsFactory().generate_custom_attributes(cads=[cad]))
    # asmt_template = rest_facade.create_asmt_template(
    #     audit, assessment_type="Control", cad_type=attr_type)
    assessment_template = _create_asmt_template(
        audit=audit, assessment_type="Control", cads=[cad])
    exp_asmt = rest_facade.create_asmt_from_template(
        audit, assessment_template, control_mapped_to_program)
    cad_created = None
    for cad_cur in exp_asmt.custom_attribute_definitions:
      if cad_cur["title"] == cad.title:
        cad_created = cad_cur
    asmts_ui_service = webui_service.AssessmentsService(selenium)
    asmts_ui_service.open_info_page_of_obj_fill_lca(exp_asmt, cavs)
    act_asmt = self.info_service().get_obj(obj=exp_asmt)
    exp_asmt.update_attrs(updated_at=act_asmt.updated_at,
                          status=unicode(object_states.IN_PROGRESS),
                          mapped_objects=[control_mapped_to_program],
                          custom_attributes=cavs,
                          custom_attribute_definitions=[cad_created])
    _assert_asmt(asmts_ui_service, exp_asmt, True)

  @pytest.mark.smoke_tests
  def test_asmts_gcas_populate(self, program, audit,
                               gcads_for_asmt, assessment, selenium):
    """Test for checking population of GCA from UI.
    Preconditions:
    - Program created via REST API.
    - Audit created via REST API.
    - Global Custom Attributes for Assessment created via REST API.
    - Assessments created via REST API.
    """
    custom_attributes = CustomAttributeDefinitionsFactory(
        ).generate_custom_attributes(gcads_for_asmt)
    asmts_ui_service = webui_service.AssessmentsService(selenium)
    asmts_ui_service.open_info_page_of_obj_fill_gca(
        assessment, custom_attributes)
    act_asmt = self.info_service().get_obj(obj=assessment)
    assessment.update_attrs(
        updated_at=act_asmt.updated_at, status=act_asmt.status,
        custom_attributes=custom_attributes,
        custom_attribute_definitions=gcads_for_asmt)
    _assert_asmt(asmts_ui_service, assessment, True)

  @pytest.mark.smoke_tests
  def test_view_evidence_urls_as_verifier(self, program, audit, selenium):
    """Test that an assessment verifier can see evidence urls
    on assessment page
    """
    verifier = rest_facade.create_user_with_role(roles.CREATOR)
    asmt = rest_facade.create_asmt(audit, verifiers=[verifier])
    asmt_service = webui_service.AssessmentsService(selenium)
    url = string_utils.StringMethods.random_string()
    asmt_service.add_evidence_urls(asmt, [url])
    users.set_current_user(verifier)
    actual_asmt = asmt_service.get_obj_from_info_page(asmt)
    asmt.update_attrs(
        status=object_states.IN_PROGRESS,
        updated_at=self.info_service().get_obj(obj=asmt).updated_at,
        evidence_urls=[url]).repr_ui()
    self.general_equal_assert(asmt, actual_asmt, "audit")

  @pytest.mark.smoke_tests
  def test_add_person_to_acl_list(self, program, audit, selenium):
    """Test that an assessment assignee can add a person to ACL"""
    assignee = rest_facade.create_user_with_role(roles.CREATOR)
    primary_contact = rest_facade.create_user_with_role(roles.CREATOR)
    asmt = rest_facade.create_asmt(audit, assignees=[assignee])
    users.set_current_user(assignee)
    asmt_service = webui_service.AssessmentsService(selenium)
    asmt_service.add_primary_contact(asmt, primary_contact)
    selenium.refresh()
    actual_asmt = asmt_service.get_obj_from_info_page(asmt)
    asmt.update_attrs(
        updated_at=rest_facade.get_obj(asmt).updated_at,
        primary_contacts=[primary_contact],
        modified_by=assignee).repr_ui()
    self.general_equal_assert(asmt, actual_asmt, "audit")


class TestRelatedAssessments(base.Test):
  """Tests for related assessments"""

  @staticmethod
  def _related_asmts_of_obj(obj, selenium):
    """Return related assessments of obj (Control or Objective)"""
    return factory.get_cls_webui_service(objects.get_plural(
        obj.type))(selenium).get_obj_related_asmts_titles(obj)

  def _assert_asmt_with_related_asmts(
      self, checked_asmt, related_asmts_titles, selenium
  ):
    """Assert that assessment `checked_asmt` on UI is the same as in
    `checked_asmt`.
    Also assert that `Asessment title`, `Related objects`, `Audit title` on
    "Related Assessments" tab are the same as in `related_asmts_titles`."""
    asmts_ui_service = webui_service.AssessmentsService(selenium)
    _assert_asmt(asmts_ui_service, checked_asmt)
    assert asmts_ui_service.get_asmt_related_asmts_titles(checked_asmt) == \
        related_asmts_titles

  @pytest.mark.smoke_tests
  @pytest.mark.parametrize(
      "assessment_type",
      ["Control", "Objective"]
  )
  def test_related_asmts(
      self, control_mapped_to_program, objective_mapped_to_program,
      audit, assessment_type, selenium
  ):
    """Objects structure:
    Program
    -> Control
    -> Objective
    -> Audit
      -> Asmt-1 mapped to Control and Objective, asmt type="assessment_type"
      -> Asmt-2 mapped to Control and Objective, asmt type="assessment_type"
    As a result, assessments are related."""
    if assessment_type == "Control":
      related_objs = [control_mapped_to_program, objective_mapped_to_program]
    else:
      related_objs = [objective_mapped_to_program, control_mapped_to_program]
    assessments = [_create_mapped_asmt(
        audit=audit, assessment_type=assessment_type,
        objs_to_map=related_objs)
        for _ in xrange(2)]
    related_asmts_titles = [
        (assessments[1].title, related_objs[0].title, audit.title)]
    self._assert_asmt_with_related_asmts(
        checked_asmt=assessments[0],
        related_asmts_titles=related_asmts_titles,
        selenium=selenium)

  @pytest.mark.smoke_tests
  def test_not_related_asmts_different_types(
      self, control_mapped_to_program, objective_mapped_to_program,
      audit, selenium
  ):
    """Objects structure:
    Program
    -> Control
    -> Objective
    -> Audit
      -> Asmt-1 mapped to Control and Objective, asmt type=Control
      -> Asmt-2 mapped to Control and Objective, asmt type=Objective
    As a result, assessments are not related."""
    assessments = [_create_mapped_asmt(
        audit=audit, assessment_type=assessment_type,
        objs_to_map=[control_mapped_to_program, objective_mapped_to_program])
        for assessment_type in ("Control", "Objective")]
    self._assert_asmt_with_related_asmts(
        checked_asmt=assessments[0],
        related_asmts_titles=[],
        selenium=selenium)

  @pytest.mark.smoke_tests
  def test_not_related_asmts_mapped_not_to_type(
      self, objective_mapped_to_program, audit, selenium
  ):
    """Objects structure:
    Program
    -> Objective
    -> Audit
      -> Asmt-1 mapped to Objective but asmt type=Control
      -> Asmt-2 mapped to Objective but asmt type=Control
    As a result, assessments are not related."""
    assessments = [_create_mapped_asmt(
        audit=audit, assessment_type="Control",
        objs_to_map=[objective_mapped_to_program])
        for _ in xrange(2)]
    self._assert_asmt_with_related_asmts(
        checked_asmt=assessments[0],
        related_asmts_titles=[],
        selenium=selenium)

  @pytest.mark.smoke_tests
  def test_related_asmts_in_different_audits_mapped_to_same_control(
      self, control_mapped_to_program, audits, selenium
  ):
    """Objects structure:
    Program
    -> Control
    -> Audit-1 -> Asmt-1 mapped to Control
    -> Audit-2 -> Asmt-2 mapped to Control
    As a result, assessments are related."""
    assessments = [_create_mapped_asmt(
        audit=audit, assessment_type="Control",
        objs_to_map=[control_mapped_to_program])
        for audit in audits]
    related_asmts_titles = [
        (assessments[1].title, control_mapped_to_program.title,
         audits[1].title)]
    self._assert_asmt_with_related_asmts(
        checked_asmt=assessments[0],
        related_asmts_titles=related_asmts_titles,
        selenium=selenium)

  @pytest.mark.smoke_tests
  def test_not_related_asmts_mapped_to_different_controls(
      self, controls_mapped_to_program, audits, selenium
  ):
    """Objects structure:
    Program
    -> Control-1
    -> Control-2
    -> Audit-1 -> Asmt-1 mapped to Control-1
    -> Audit-2 -> Asmt-2 mapped to Control-2
    As a result, assessments are not related."""
    assessments = [_create_mapped_asmt(
        audit=audit, assessment_type="Control", objs_to_map=[control])
        for control, audit in zip(controls_mapped_to_program, audits)]
    self._assert_asmt_with_related_asmts(
        checked_asmt=assessments[0],
        related_asmts_titles=[],
        selenium=selenium)

  @pytest.mark.smoke_tests
  def test_related_asmts_in_different_audits_mapped_to_mapped_controls(
      self, program, selenium
  ):
    """Objects structure:
    Program
    -> Control-1
    -> Control-2
    Control-1 and Control-2 are mapped.
    -> Audit-1 -> Asmt-1 mapped to Control-1
    -> Audit-2 -> Asmt-2 mapped to Control-2
    As a result, assessments are related."""
    controls = [rest_facade.create_control(program) for _ in xrange(2)]
    rest_facade.map_objs(controls[0], controls[1])
    audits = [rest_facade.create_audit(program) for _ in xrange(2)]
    assessments = [_create_mapped_asmt(
        audit=audit, assessment_type="Control", objs_to_map=[control])
        for control, audit in zip(controls, audits)]
    related_asmts_titles = [
        (assessments[1].title, controls[1].title, audits[1].title)]
    self._assert_asmt_with_related_asmts(
        checked_asmt=assessments[0],
        related_asmts_titles=related_asmts_titles,
        selenium=selenium)

  @pytest.mark.smoke_tests
  def test_related_asmts_on_control_page(
      self, control_mapped_to_program, audits, selenium
  ):
    """Objects structure:
    Program
    -> Control
    -> Audit-1 -> Asmt-1 mapped to Control
    -> Audit-2 -> Asmt-2 mapped to Control
    Check Related Assessments on Control's page"""
    assessments = [_create_mapped_asmt(
        audit=audit, assessment_type="Control",
        objs_to_map=[control_mapped_to_program])
        for audit in audits]
    related_asmts_titles = [
        (assessment.title, control_mapped_to_program.title,
         assessment.audit['title']) for assessment in assessments]
    assert self._related_asmts_of_obj(control_mapped_to_program, selenium) ==\
        related_asmts_titles[::-1]

  @pytest.mark.smoke_tests
  @pytest.mark.parametrize(
      "obj",
      ["control_mapped_to_program", "objective_mapped_to_program"],
      indirect=True
  )
  def test_related_asmts_on_obj_page(
      self, obj, audit, selenium
  ):
    """Objects structure:
    Program
    -> Obj (Control or Objective)
    -> Audit
      -> Asmt-1 mapped to Obj, asmt type="obj_type"
      -> Asmt-2 mapped to Obj, asmt type="obj_type"
    Check Related Assessments on Obj's page"""
    assessments = [_create_mapped_asmt(
        audit=audit, assessment_type=obj.type, objs_to_map=[obj])
        for _ in xrange(2)]
    related_asmts_titles = [
        (assessment.title, obj.title, audit.title)
        for assessment in assessments]
    assert self._related_asmts_of_obj(obj, selenium) ==\
        related_asmts_titles[::-1]


class TestRelatedIssues(base.Test):
  """Tests for related issues"""

  def _assert_asmt_with_related_issues(
      self, checked_asmt, related_issues_titles, selenium
  ):
    """Assert that assessment `checked_asmt` on UI is the same as in
    `checked_asmt`.
    Also assert that `Issues title` on "Related Issues" tab are
    the same as in `related_issues_titles`."""
    asmts_ui_service = webui_service.AssessmentsService(selenium)
    _assert_asmt(asmts_ui_service, checked_asmt)
    assert asmts_ui_service.get_related_issues_titles(
        checked_asmt) == related_issues_titles

  def _create_asmt_mapped_to_control_mapped_to_issue(
      self, asmt_type, audit, control, issue
  ):
    """Map 'control' to 'issue'.
    Return create assessment with 'asmt_type' and map to 'control'."""
    rest_facade.map_objs(control, issue)
    return _create_mapped_asmt(
        audit=audit, assessment_type=asmt_type,
        objs_to_map=[control])

  @pytest.mark.smoke_tests
  @pytest.mark.parametrize(
      "assessment_type",
      ["Control", "Objective"]
  )
  def test_related_issues_on_different_asmt_types(
      self, assessment_type, control_mapped_to_program,
      issue_mapped_to_program, audit, selenium
  ):
    """Objects structure:
    Program
    -> Control. Map it to issue
    -> Audit
      -> Asmt-1 with type Control. Map to Control.
      -> Asmt-2 with type Objective. Map to Control.
    As a result, Asmt-1 has related issue
      and Asmt-2 doesn't have related issue."""
    assessment = self._create_asmt_mapped_to_control_mapped_to_issue(
        assessment_type, audit, control_mapped_to_program,
        issue_mapped_to_program)
    exp_related_issues_titles = []
    if assessment_type == "Control":
      exp_related_issues_titles = [issue_mapped_to_program.title]
    self._assert_asmt_with_related_issues(
        checked_asmt=assessment,
        related_issues_titles=exp_related_issues_titles,
        selenium=selenium)
