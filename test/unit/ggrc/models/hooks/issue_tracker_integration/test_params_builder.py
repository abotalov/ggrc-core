# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Test Issue tracker query builder."""

# pylint: disable=protected-access
# pylint: disable=invalid-name

import unittest

import ddt
import mock

from ggrc.models import exceptions
from ggrc.models.hooks.issue_tracker import integration_utils
from ggrc.models.hooks.issue_tracker import issue_tracker_params_builder \
    as params_builder


@ddt.ddt
class TestBaseIssueTrackerParamsBuilder(unittest.TestCase):
  """Test base class for issue tracker params builder."""

  def setUp(self):
    """Perform initialisation for each test cases."""
    self.builder = params_builder.BaseIssueTrackerParamsBuilder()

  @ddt.data(
      {"component_id": "not float number"},
      {"hotlist_id": "not float number"},
  )
  def test_handle_issue_tracker_info_for_failure(self, issue_tracker_info):
    """Test 'handle_issue_tracker_info' method for failure cases."""
    mock_object = mock.MagicMock()
    with self.assertRaises(exceptions.ValidationError):
      self.builder.handle_issue_tracker_info(mock_object, issue_tracker_info)

  def test_handle_issue_tracker_info(self):
    """Test 'handle_issue_tracker_info' method."""
    # Arrange test data.
    mock_object = mock.MagicMock()
    issue_tracker_info = {
        "component_id": "123",
        "hotlist_id": 321,
        "title": "test_title",
        "issue_type": "test_type",
        "issue_priority": "P2",
        "issue_severity": "S2",
    }
    expected_result = {
        "component_id": 123,
        "hotlist_ids": [321, ],
        "title": "test_title",
        "type": "test_type",
        "priority": "P2",
        "severity": "S2",
    }

    # Perform action.
    self.builder.handle_issue_tracker_info(mock_object, issue_tracker_info)

    # Assert results.
    self.assertEquals(
        self.builder.params.get_issue_tracker_params(),
        expected_result
    )


@ddt.ddt
class TestIssueQueryBuilder(unittest.TestCase):
  """Test issue tracker builder for iisue object."""

  def setUp(self):
    """Perform initialisation for each test cases."""
    self.builder = params_builder.IssueParamsBuilder()

  def test_handle_issue_attributes(self):
    """Test '_handle_issue_attributes' method."""
    # pylint: disable=protected-access
    # Arrange test data.
    mock_object = mock.MagicMock()
    mock_object.description = "<p>test_description</p>"
    mock_object.test_plan = "<p>test_plan</p>"
    expected_result = {
        "comment": "Following is the issue Description from GGRC: "
                   "test_description\n\n"
                   "Following is the issue Remediation Plan from GGRC: "
                   "test_plan"
    }

    # Perform action.
    self.builder._handle_issue_comment_attributes(mock_object)

    # Assert results.
    self.assertEquals(
        self.builder.params.get_issue_tracker_params(),
        expected_result
    )

  def test_handle_people_emails_without_ccs(self):
    """Test '_handle_people_emails' method without emails in ccs list."""
    mock_object = mock.MagicMock()
    mock_object.modified_by.email = "reporter_email"

    verifier = mock.MagicMock()
    verifier.person.name = "admin_name"
    verifier.person.email = "verifier_email"
    verifier.ac_role.name = "Admin"

    assignee = mock.MagicMock()
    assignee.person.name = "assignee_name"
    assignee.person.email = "assignee_email"
    assignee.ac_role.name = "Primary Contacts"

    access_control_list = [verifier, assignee, ]
    mock_object.access_control_list = access_control_list
    allowed_emails = {acl.person.email for acl in access_control_list}

    expected_result = {
        "verifier": "verifier_email",
        "assignee": "assignee_email",
        "reporter": "reporter_email",
        "ccs": [],
    }

    # Perform action.
    self.builder._handle_people_emails(mock_object, allowed_emails)

    # Assert results.
    self.assertDictEqual(
        self.builder.params.get_issue_tracker_params(),
        expected_result
    )

  def test_handle_people_emails_with_ccs(self):
    """Test '_handle_people_emails' method with emails in ccs list."""
    # Arrange test data.
    mock_object = mock.MagicMock()
    mock_object.modified_by.email = "reporter_email"

    verifier_1 = mock.MagicMock()
    verifier_1.person.name = "admin_name"
    verifier_1.person.email = "verifier_email_1"
    verifier_1.ac_role.name = "Admin"

    verifier_2 = mock.MagicMock()
    verifier_2.person.name = "verifier_name"
    verifier_2.person.email = "verifier_email_2"
    verifier_2.ac_role.name = "Admin"

    assignee_1 = mock.MagicMock()
    assignee_1.person.name = "assignee_name"
    assignee_1.person.email = "assignee_email_1"
    assignee_1.ac_role.name = "Primary Contacts"

    assignee_2 = mock.MagicMock()
    assignee_2.person.name = "primary_contact_name"
    assignee_2.person.email = "assignee_email_2"
    assignee_2.ac_role.name = "Primary Contacts"

    custom_role_1 = mock.MagicMock()
    custom_role_1.person.name = "reporter_name"
    custom_role_1.person.email = "reporter_email"
    custom_role_1.ac_role.name = "Custom Role"

    custom_role_2 = mock.MagicMock()
    custom_role_2.person.name = "custom_name"
    custom_role_2.person.email = "custom_email"
    custom_role_2.ac_role.name = "Custom Role"

    custom_role_3 = mock.MagicMock()
    custom_role_3.person.name = "admin_name"
    custom_role_3.person.email = "verifier_email_1"
    custom_role_3.ac_role.name = "Custom Role"

    access_control_list = [
        verifier_1,
        verifier_2,
        assignee_1,
        assignee_2,
        custom_role_1,
        custom_role_2,
        custom_role_3,
    ]
    allowed_emails = {acl.person.email for acl in access_control_list}
    mock_object.access_control_list = access_control_list

    expected_result = {
        "verifier": "verifier_email_1",
        "assignee": "assignee_email_1",
        "reporter": "reporter_email",
        "ccs": ["custom_email", "verifier_email_2", "assignee_email_2"],
    }

    # Perform action.
    self.builder._handle_people_emails(mock_object, allowed_emails)

    # Assert results.
    self.assertDictEqual(
        self.builder.params.get_issue_tracker_params(),
        expected_result
    )

  def test_update_issue_comment_attributes(self):
    """Test '_update_issue_comment_attributes' method."""
    # Arrange test data.
    mock_current_object = mock.MagicMock()
    mock_current_object.description = "description"
    mock_current_object.test_plan = "test plan"

    mock_new_object = mock.MagicMock()
    mock_new_object.description = "new description"
    mock_new_object.test_plan = "new test plan"

    mock_current_tracker_info = {"enabled": True}
    mock_new_tracker_info = {"enabled": False}

    expected_result = {
        "comment": "Issue Description has been updated.\nnew description\n\n"
        "Issue Remediation Plan has been updated.\nnew test plan\n\n"
        "Changes to this GGRC object will no longer "
        "be tracked within this bug."
    }

    # Perform action.
    self.builder._update_issue_comment_attributes(mock_new_object,
                                                  mock_current_object,
                                                  mock_new_tracker_info,
                                                  mock_current_tracker_info)

    # Assert results.
    self.assertEquals(
        self.builder.params.get_issue_tracker_params(),
        expected_result
    )

  @mock.patch.object(params_builder.BaseIssueTrackerParamsBuilder,
                     "get_ggrc_object_url",
                     return_value="http://issue_url.com")
  def test_build_create_issue_tracker_params(self, url_builder_mock):
    """Test 'build_create_issue_tracker_params' method."""
    # Arrange test data.
    mock_object = mock.MagicMock()
    mock_object.modified_by.email = "reporter@email.com"
    mock_object.test_plan = "<p>test plan</p>"
    mock_object.description = "<p>description</p>"

    issue_tracker_info = {
        "enabled": True,
        "component_id": "1234",
        "hotlist_id": "4321",
        "issue_type": "PROCESS",
        "issue_priority": "P2",
        "issue_severity": "S2",
        "title": "Issue title",
    }
    expected_result = {
        "comment": "This bug was auto-generated to track a GGRC Issue. "
                   "Use the following link to find the Issue - "
                   "http://issue_url.com.\n\n"
                   "Following is the issue Description from GGRC: "
                   "description\n\n"
                   "Following is the issue Remediation Plan from GGRC: "
                   "test plan",
        "component_id": 1234,
        "hotlist_ids": [4321, ],
        "priority": "P2",
        "reporter": "reporter@email.com",
        "assignee": "",
        "verifier": "",
        "ccs": [],
        "severity": "S2",
        "status": "ASSIGNED",
        "title": "Issue title",
        "type": "PROCESS",
    }

    # Perform action.
    with mock.patch.object(
        integration_utils,
        "exclude_auditor_emails",
        return_value={"reporter@email.com", }
    ) as exclude_emails_mock:
      params = self.builder.build_create_issue_tracker_params(
          mock_object,
          issue_tracker_info
      )

    # Assert results.
    exclude_emails_mock.assert_called_with({"reporter@email.com", })
    url_builder_mock.assert_called_once()
    self.assertDictEqual(params.get_issue_tracker_params(), expected_result)

  def test_build_delete_params(self):
    """Test 'build_delete_params' method."""
    expected_result = {
        "comment": "GGRC object has been deleted. GGRC changes will "
                   "no longer be tracked within this bug."
    }
    self.builder.build_delete_issue_tracker_params()
    self.assertEquals(
        self.builder.params.get_issue_tracker_params(),
        expected_result
    )
