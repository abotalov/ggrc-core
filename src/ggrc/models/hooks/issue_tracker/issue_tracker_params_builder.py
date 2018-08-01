# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""This module contains functionality for building Issue tracker query."""

# pylint: disable=invalid-name

import urlparse

import html2text

from ggrc import utils as ggrc_utils
from ggrc.models.hooks.issue_tracker import integration_utils
from ggrc.models.hooks.issue_tracker import \
    issue_tracker_params_container as params_container


class BaseIssueTrackerParamsBuilder(object):
  """Base issue tracker params builder class.

  This class and all classes which inherits from it provide
  functionality for building query to issue tracker.
  So, this classes encapsulate business logic for mapping GGRC objects fields
  to issue tracker issue fields.
  """

  INITIAL_COMMENT_TMPL = (
      u"This bug was auto-generated to track a GGRC {model}. "
      "Use the following link to find the {model} - {link}."
  )

  DELETE_TMPL = (
      u"GGRC object has been deleted. GGRC changes will "
      "no longer be tracked within this bug."
  )

  DISABLE_TMPL = (
      u"Changes to this GGRC object will no longer be tracked within this bug."
  )

  ENABLE_TMPL = (
      u"Changes to this GGRC object will be tracked within this bug."
  )

  COMMENT_TMPL = (
      u"A new comment is added by '{author}' to the '{model}': '{comment}'.\n"
      "Use the following to link to get more information from the "
      "GGRC '{model}'. Link - {link}"
  )

  ISSUE_TRACKER_INFO_FIELDS_TO_CHECK = (
      "component_id",
      "hotlist_id",
      "issue_severity",
      "issue_priority",
      "enabled",
  )

  def __init__(self):
    """Basic initialization."""
    self.params = params_container.IssueTrackerParamsContainer()

  @staticmethod
  def get_ggrc_object_url(obj):
    """Builds and returns URL to GGRC object."""
    return urlparse.urljoin(
        ggrc_utils.get_url_root(),
        ggrc_utils.view_url_for(obj)
    )

  def handle_issue_tracker_info(self, obj, issue_tracker_info):
    """Handle issue tracker information."""
    self.params.component_id = issue_tracker_info.get("component_id")
    self.params.hotlist_id = issue_tracker_info.get("hotlist_id")
    self.params.title = issue_tracker_info.get("title", obj.title)
    self.params.issue_type = issue_tracker_info.get("issue_type")
    self.params.issue_priority = issue_tracker_info.get("issue_priority")
    self.params.issue_severity = issue_tracker_info.get("issue_severity")
    self.params.enabled = issue_tracker_info.get("enabled")

  def _update_issue_tracker_info(self, new_issue_tracker_info,
                                 current_issue_tracker_info):
    """Update issue tracker information."""

    fields_to_check = self.ISSUE_TRACKER_INFO_FIELDS_TO_CHECK

    for field in fields_to_check:
      new_value = new_issue_tracker_info.get(field)
      old_value = current_issue_tracker_info.get(field)
      if new_value != old_value:
        setattr(self.params, field, new_value)


class IssueParamsBuilder(BaseIssueTrackerParamsBuilder):
  """Issue tracker query builder for GGRC Issue object."""

  MODEL_NAME = "Issue"

  ASSIGNED_ISSUE_STATUS = "ASSIGNED"

  DESCRIPTION_TMPL = u"Following is the issue Description from GGRC: {}"
  REMEDIATION_PLAN_TMPL = (
      u"Following is the issue Remediation Plan from GGRC: {}"
  )
  UPDATE_DESCRIPTION_TMPL = (
      u"Issue Description has been updated.\n{}"
  )
  UPDATE_REMEDIATION_PLAN_TMPL = (
      u"Issue Remediation Plan has been updated.\n{}"
  )
  EXCLUDE_REPORTER_EMAIL_ERROR_MSG = (
      u"Issue tracker integration is not activated because the reporter "
      "is an Global auditor."
  )

  def build_create_issue_tracker_params(self, obj, issue_tracker_info):
    """Build create issue query for issue tracker."""
    all_emails = {acl.person.email for acl in obj.access_control_list}

    # Add the person who triggered the event.
    all_emails |= {obj.modified_by.email}
    allowed_emails = integration_utils.exclude_auditor_emails(all_emails)

    # Don't turn on integration if 'reporter' is auditor.
    reporter_email = obj.modified_by.email
    if reporter_email not in allowed_emails:
      obj.add_warning(self.EXCLUDE_REPORTER_EMAIL_ERROR_MSG)
      return self.params

    self.params.status = self.ASSIGNED_ISSUE_STATUS
    self.params.add_comment(self.INITIAL_COMMENT_TMPL.format(
        model=self.MODEL_NAME,
        link=self.get_ggrc_object_url(obj)
    ))

    self.handle_issue_tracker_info(obj, issue_tracker_info)
    self._handle_people_emails(obj, allowed_emails)
    self._handle_issue_comment_attributes(obj)

    return self.params

  def build_update_issue_tracker_params(self,
                                        obj,
                                        initial_state,
                                        new_issue_tracker_info,
                                        current_issue_tracker_info):
    """Build update issue query for issue tracker."""

    if (not new_issue_tracker_info["enabled"] and
            not current_issue_tracker_info["enabled"]):
      return self.params

    self._update_issue_tracker_info(new_issue_tracker_info,
                                    current_issue_tracker_info)

    self._update_issue_comment_attributes(obj,
                                          initial_state,
                                          new_issue_tracker_info,
                                          current_issue_tracker_info)

    return self.params

  def build_delete_issue_tracker_params(self):
    """Build delete issue query for issue tracker."""
    self.params.add_comment(self.DELETE_TMPL.format(model="Issue"))

    return self.params

  def build_params_for_comment(self, sync_obj, comment, author):
    """Build query to Issue tracker for adding comment to issue."""
    comment = html2text.HTML2Text().handle(comment).strip("\n")
    self.params.add_comment(self.COMMENT_TMPL.format(
        author=author,
        comment=comment,
        model=sync_obj.__class__.__name__,
        link=self.get_ggrc_object_url(sync_obj),
    ))
    return self.params

  def _handle_people_emails(self, obj, allowed_emails):
    """Handle emails.

    Reporter should be a person who triggers an event.
    Verifier should be first person from Admins in alphabetical order.
    Assignee should be first person from Primary Contacts
             in alphabetical order.
    CCS should be all other persons that mentioned in custom roles.

    No field should contain global auditors.
    """
    acls = obj.access_control_list

    # Handle Admins list.
    admins = [acl.person for acl in acls
              if acl.ac_role.name == "Admin" and
              acl.person.email in allowed_emails]
    admins = sorted(admins, key=lambda person: person.name)

    issue_verifier_email = admins[0].email if admins else ""
    self.params.verifier = issue_verifier_email

    # Handle Primary Contacts list.
    primary_contacts = [
        acl.person for acl in acls
        if acl.ac_role.name == "Primary Contacts" and
        acl.person.email in allowed_emails
    ]
    primary_contacts = sorted(primary_contacts, key=lambda p: p.name)
    assignee_email = primary_contacts[0].email if primary_contacts else ""
    self.params.assignee = assignee_email

    # Handle reporter list.
    reporter_email = obj.modified_by.email
    self.params.reporter = reporter_email

    # Handle CCS list.
    ccs = allowed_emails - {issue_verifier_email,
                            assignee_email,
                            reporter_email}
    self.params.cc_list = list(ccs)

  def _handle_issue_comment_attributes(self, obj):
    """Handle attributes from GGRC Issue object.

    This method adds Issue description and Remediation Plan as comments
    to Issue Tracker Issue.
    """
    description = obj.description
    if description:
      description = html2text.HTML2Text().handle(description).strip("\n")
      self.params.add_comment(self.DESCRIPTION_TMPL.format(description))

    test_plan = obj.test_plan
    if test_plan:
      test_plan = html2text.HTML2Text().handle(test_plan).strip("\n")
      self.params.add_comment(self.REMEDIATION_PLAN_TMPL.format(test_plan))

  def _update_issue_comment_attributes(self, obj, initial_state,
                                       new_issue_tracker_info,
                                       current_issue_tracker_info):
    """Update issue tracker comments"""
    description = obj.description
    initial_description = initial_state.description
    if description != initial_description:
      description = html2text.HTML2Text().handle(description).strip("\n")
      self.params.add_comment(self.UPDATE_DESCRIPTION_TMPL.format(description))

    test_plan = obj.test_plan
    initial_test_plan = initial_state.test_plan
    if test_plan != initial_test_plan:
      test_plan = html2text.HTML2Text().handle(test_plan).strip("\n")
      self.params.add_comment(
          self.UPDATE_REMEDIATION_PLAN_TMPL.format(test_plan)
      )

    old_enabled = current_issue_tracker_info["enabled"]
    new_enabled = new_issue_tracker_info["enabled"]
    if old_enabled != new_enabled:
      enabled = new_enabled
      comment = self.ENABLE_TMPL if enabled else self.DISABLE_TMPL
      self.params.add_comment(comment)
