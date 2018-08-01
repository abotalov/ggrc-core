# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Integration tests for Issue with IssueTracker integration."""

# pylint: disable=unused-argument

import mock
import ddt

from ggrc import models
from ggrc import settings
from ggrc.models import all_models
from ggrc.models.hooks.issue_tracker import integration_utils
from ggrc.models.hooks.issue_tracker import issue_tracker_params_builder \
    as params_builder
from ggrc.integrations import integrations_errors

from integration.ggrc.models import factories
from integration import ggrc
from integration.ggrc.api_helper import Api


@ddt.ddt
class TestIssueIntegration(ggrc.TestCase):
  """Test set for IssueTracker integration functionality."""

  # pylint: disable=invalid-name

  def setUp(self):
    # pylint: disable=super-on-old-class
    super(TestIssueIntegration, self).setUp()
    self.api = Api()
    self.client.get("/login")

  @mock.patch("ggrc.integrations.issues.Client.create_issue",
              return_value={"issueId": "issueId"})
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_create_issue_tracker_info(self, mock_create_issue):
    """Test creation issue tracker issue for Issue object."""
    component_id = "1234"
    hotlist_id = "4321"
    issue_type = "Default Issue type"
    issue_priority = "P2"
    issue_severity = "S1"
    title = "test title"

    with mock.patch.object(integration_utils, "exclude_auditor_emails",
                           return_value={u"user@example.com", }):
      response = self.api.post(all_models.Issue, {
          "issue": {
              "title": title,
              "context": None,
              "issue_tracker": {
                  "enabled": True,
                  "component_id": int(component_id),
                  "hotlist_id": int(hotlist_id),
                  "issue_type": issue_type,
                  "issue_priority": issue_priority,
                  "issue_severity": issue_severity,
              }
          },
      })
      mock_create_issue.assert_called_once()
      self.assertEqual(response.status_code, 201)
      issue_id = response.json.get("issue").get("id")
      issue_tracker_issue = models.IssuetrackerIssue.get_issue("Issue",
                                                               issue_id)
      self.assertTrue(issue_tracker_issue.enabled)
      self.assertEqual(issue_tracker_issue.title, title)
      self.assertEqual(issue_tracker_issue.component_id, component_id)
      self.assertEqual(issue_tracker_issue.hotlist_id, hotlist_id)
      self.assertEqual(issue_tracker_issue.issue_type, issue_type)
      self.assertEqual(issue_tracker_issue.issue_priority, issue_priority)
      self.assertEqual(issue_tracker_issue.issue_severity, issue_severity)

  def test_exclude_auditor(self):
    """Test 'exclude_auditor_emails' util."""
    audit = factories.AuditFactory()
    factories.AccessControlListFactory(
        ac_role=factories.AccessControlRoleFactory(name="Auditors"),
        person=factories.PersonFactory(email="auditor@example.com"),
        object_id=audit.id,
        object_type="Audit"
    )

    result = integration_utils.exclude_auditor_emails(["auditor@example.com",
                                                       "admin@example.com"])
    self.assertEqual(result, {"admin@example.com", })

  @ddt.data(
      ({"description": "new description"},
       {"comment": "Issue Description has been updated.\nnew description"}),
      ({"test_plan": "new test plan"},
       {"comment": "Issue Remediation Plan has been updated.\nnew test plan"}),
      ({"issue_tracker": {"component_id": "123", "enabled": True}},
       {"component_id": 123}),
      ({"issue_tracker": {"hotlist_id": "321", "enabled": True}},
       {"hotlist_ids": [321, ]}),
      ({"issue_tracker": {"issue_priority": "P2", "enabled": True}},
       {"priority": "P2"}),
      ({"issue_tracker": {"issue_severity": "S2", "enabled": True}},
       {"severity": "S2"}),
      ({"issue_tracker": {"enabled": False}},
       {"comment": "Changes to this GGRC object will no longer be "
                   "tracked within this bug."}),
  )
  @ddt.unpack
  @mock.patch("ggrc.integrations.issues.Client.update_issue")
  def test_update_issue(self, issue_attrs, expected_query, mock_update_issue):
    """Test updating issue tracker issue."""
    iti = factories.IssueTrackerIssueFactory(
        enabled=True,
        issue_tracked_obj=factories.IssueFactory()
    )
    with mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True):
      self.api.put(iti.issue_tracked_obj, issue_attrs)
    mock_update_issue.assert_called_with(iti.issue_id, expected_query)

  @ddt.data(
      {"notes": "new notes"},
      {"end_date": "2018-07-15"},
      {"start_date": "2018-07-15"},
  )
  @mock.patch("ggrc.integrations.issues.Client.update_issue")
  def test_update_issue_with_untracked_fields(self, issue_attrs,
                                              mock_update_issue):
    """Test updating issue with fields which shouldn't be sync."""
    iti = factories.IssueTrackerIssueFactory(
        enabled=True,
        issue_tracked_obj=factories.IssueFactory()
    )
    with mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True):
      self.api.put(iti.issue_tracked_obj, issue_attrs)
    mock_update_issue.assert_not_called()

  @mock.patch("ggrc.integrations.issues.Client.update_issue")
  def test_delete_issue(self, mock_update_issue):
    """Test updating issue tracker issue when issue in GGRC has been deleted"""
    iti = factories.IssueTrackerIssueFactory(
        enabled=True,
        issue_tracked_obj=factories.IssueFactory()
    )
    expected_query = {"comment": "GGRC object has been deleted. GGRC changes "
                                 "will no longer be tracked within this bug."}
    with mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True):
      self.api.delete(iti.issue_tracked_obj)
    mock_update_issue.assert_called_with(iti.issue_id, expected_query)

  @mock.patch.object(params_builder.BaseIssueTrackerParamsBuilder,
                     "get_ggrc_object_url",
                     return_value="http://issue_url.com")
  @mock.patch("ggrc.integrations.issues.Client.update_issue")
  def test_adding_comment_to_issue(self, update_issue_mock, url_builder_mock):
    """Test adding comment to issue."""
    iti = factories.IssueTrackerIssueFactory(
        enabled=True,
        issue_tracked_obj=factories.IssueFactory()
    )
    comment = factories.CommentFactory(description="test comment")

    expected_result = {
        "comment": u"A new comment is added by 'Example User' to the 'Issue': "
                   u"'test comment'.\nUse the following to link to get more "
                   u"information from the GGRC 'Issue'. Link - "
                   u"http://issue_url.com"
    }

    with mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True):
      self.api.post(all_models.Relationship, {
          "relationship": {
              "source": {"id": iti.issue_tracked_obj.id, "type": "Issue"},
              "destination": {"id": comment.id, "type": "comment"},
              "context": None
          },
      })
    url_builder_mock.assert_called_once()
    update_issue_mock.assert_called_with(iti.issue_id, expected_result)


@ddt.ddt
class TestDisabledIssueIntegration(ggrc.TestCase):
  """Tests for IssueTracker integration functionality with disabled sync."""

  # pylint: disable=invalid-name

  def setUp(self):
    # pylint: disable=super-on-old-class
    super(TestDisabledIssueIntegration, self).setUp()
    self.api = Api()
    self.client.get("/login")

  @mock.patch("ggrc.integrations.issues.Client.create_issue")
  def test_issue_creation(self, mock_create_issue):
    """Test creating Issue object with disabled integration."""
    with mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True):
      response = self.api.post(all_models.Issue, {
          "issue": {
              "title": "test title",
              "context": None,
              "issue_tracker": {
                  "enabled": False,
              }
          },
      })
    mock_create_issue.assert_not_called()
    self.assertEqual(response.status_code, 201)
    issue_id = response.json.get("issue").get("id")
    issue_tracker_issue = models.IssuetrackerIssue.get_issue("Issue",
                                                             issue_id)
    self.assertIsNone(issue_tracker_issue)

  @mock.patch("ggrc.integrations.issues.Client.update_issue")
  def test_issue_deletion(self, mock_update_issue):
    """Test deleting Issue object with disabled integration for issue."""
    iti = factories.IssueTrackerIssueFactory(
        enabled=False,
        issue_tracked_obj=factories.IssueFactory()
    )
    with mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True):
      self.api.delete(iti.issue_tracked_obj)
    mock_update_issue.assert_not_called()

  @ddt.data(
      {"description": "new description", "issue_tracker": {"enabled": False}},
      {"test_plan": "new test plan", "issue_tracker": {"enabled": False}},
      {"issue_tracker": {"component_id": "123", "enabled": False}},
      {"issue_tracker": {"hotlist_id": "321", "enabled": False}},
      {"issue_tracker": {"issue_priority": "P2", "enabled": False}},
      {"issue_tracker": {"issue_severity": "S2", "enabled": False}},
  )
  @mock.patch("ggrc.integrations.issues.Client.update_issue")
  def test_update_issue_object(self, issue_attrs, mock_update_issue):
    """Test updating issue object with disabled integration for issue."""
    iti = factories.IssueTrackerIssueFactory(
        enabled=False,
        issue_tracked_obj=factories.IssueFactory()
    )
    with mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True):
      self.api.put(iti.issue_tracked_obj, issue_attrs)
    mock_update_issue.assert_not_called()

  @mock.patch("ggrc.integrations.issues.Client.create_issue",
              side_effect=[integrations_errors.Error, {"issueId": "issueId"}])
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_issue_recreation(self, mock_create_issue):
    """Test retrying to turn on integration after failed creation."""
    # Arrange data.
    component_id = "1234"
    hotlist_id = "4321"
    issue_type = "Default Issue type"
    issue_priority = "P2"
    issue_severity = "S1"
    title = "test title"
    issue_tracker_attrs = {
        "enabled": True,
        "component_id": int(component_id),
        "hotlist_id": int(hotlist_id),
        "issue_type": issue_type,
        "issue_priority": issue_priority,
        "issue_severity": issue_severity,
    }

    # Perform actions and assert results.
    with mock.patch.object(integration_utils, "exclude_auditor_emails",
                           return_value={u"user@example.com", }):

      # Try to create issue. create_issue should raise exception here.
      response = self.api.post(all_models.Issue, {
          "issue": {
              "title": title,
              "context": None,
              "issue_tracker": issue_tracker_attrs
          },
      })

      issue_id = response.json.get("issue").get("id")
      issue_tracker_issue = models.IssuetrackerIssue.get_issue("Issue",
                                                               issue_id)
      self.assertIsNone(issue_tracker_issue.issue_id)
      self.assertIsNone(issue_tracker_issue.issue_url)

      # Try to turn on integration on already created issue.
      self.api.put(
          issue_tracker_issue.issue_tracked_obj,
          {"issue_tracker": issue_tracker_attrs}
      )

      issue_id = issue_tracker_issue.issue_tracked_obj.id
      issue_tracker_issue = models.IssuetrackerIssue.get_issue("Issue",
                                                               issue_id)
      self.assertEqual(issue_tracker_issue.issue_url, "http://issue/issueId")

  @mock.patch("ggrc.integrations.issues.Client.update_issue")
  def test_adding_comment_to_issue(self, update_issue_mock):
    """Test not adding comment to issue when issue tracker disabled."""
    iti = factories.IssueTrackerIssueFactory(
        enabled=False,
        issue_tracked_obj=factories.IssueFactory()
    )
    comment = factories.CommentFactory(description="test comment")

    with mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True):
      self.api.post(all_models.Relationship, {
          "relationship": {
              "source": {"id": iti.issue_tracked_obj.id, "type": "Issue"},
              "destination": {"id": comment.id, "type": "comment"},
              "context": None
          },
      })
    update_issue_mock.assert_not_called()
