# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>


"""Tests for assessment templates export."""
import ddt

from integration.ggrc.models import factories
from integration.ggrc import TestCase


@ddt.ddt
class TestAssessmentTemplatesExport(TestCase):
  """Assessment Template export test"""

  def setUp(self):
    """Set up for Assessment Template test cases."""
    super(TestAssessmentTemplatesExport, self).setUp()
    self.client.get("/login")

  @ddt.data(
      ("Object Admins", "Admin"),
      ("Audit Captain", "Audit Lead"),
      ("Auditors", "Auditors"),
      ("Principal Assignees", "Principal Assignees"),
      ("Secondary Assignees", "Secondary Assignees"),
      ("Primary Contacts", "Primary Contacts"),
      ("Secondary Contacts", "Secondary Contacts")
  )
  @ddt.unpack
  def test_people_labels_export(self, title, label):
    """Test for check people label export"""
    default_people = {"assignees": label, "verifiers": label}
    factories.AssessmentTemplateFactory(
        title=title,
        default_people=default_people
    )
    data = [{
        "object_name": "AssessmentTemplate",
        "filters": {
            "expression": {},
        },
        "fields": "all",
    }]

    response = self.export_parsed_csv(data)
    assessment_template = response["Assessment Template"][0]
    self.assertEqual(assessment_template["Default Assignees*"], title)
    self.assertEqual(assessment_template["Default Verifiers"], title)

  def test_empty_people_export(self):
    """Test for check people label export"""
    default_people = {"assignees": "Auditors", "verifiers": None}
    factories.AssessmentTemplateFactory(
        title="Audit Lead",
        default_people=default_people
    )
    data = [{
        "object_name": "AssessmentTemplate",
        "filters": {
            "expression": {},
        },
        "fields": "all",
    }]

    response = self.export_parsed_csv(data)
    assessment_template = response["Assessment Template"][0]
    self.assertEqual(assessment_template["Default Assignees*"], "Auditors")
    self.assertEqual(assessment_template["Default Verifiers"], "--")
