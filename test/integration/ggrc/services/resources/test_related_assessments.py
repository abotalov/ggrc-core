# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests for /api/related_assessments endpoint.

These tests only check the data returned by related assessments endpoint.
There are other tests for verifying completeness of the results and that focus
more on verifying the related SQL query.
"""

import mock
import ddt

from ggrc import db
from ggrc import views
from integration.ggrc.models import factories
from integration.ggrc.services import TestCase


@ddt.ddt
class TestRelatedAssessments(TestCase):
  """Tests for special people api endpoints."""

  URL_BASE = "/api/related_assessments"

  def setUp(self):
    super(TestRelatedAssessments, self).setUp()
    self.client.get("/login")
    with factories.single_commit():
      self.assessment1 = factories.AssessmentFactory(title="A_1")
      self.assessment2 = factories.AssessmentFactory(title="A_2")
      self.control = factories.ControlFactory()
      snap1 = self._create_snapshots(self.assessment1.audit, [self.control])
      snap2 = self._create_snapshots(self.assessment2.audit, [self.control])
      factories.RelationshipFactory(
          source=snap1[0],
          destination=self.assessment1
      )
      factories.RelationshipFactory(
          destination=snap2[0],
          source=self.assessment2,
      )
      factories.RelationshipFactory(
          source=self.assessment1.audit,
          destination=self.assessment1,
      )
      factories.RelationshipFactory(
          destination=self.assessment2.audit,
          source=self.assessment2,
      )

  def _get_related_assessments(self, obj, **kwargs):
    """Helper for retrieving assessment related objects."""
    kwargs["object_type"] = obj.type
    kwargs["object_id"] = obj.id
    return self.client.get(self.URL_BASE, query_string=kwargs)

  @ddt.data("2018-06-06 16:38:17", None)
  def test_verified_status(self, verified_date):
    """Test verified flag defines correctly"""
    self.assessment2.verified_date = verified_date
    db.session.commit()
    response = self._get_related_assessments(self.assessment1).json
    self.assertEqual(bool(verified_date), response["data"][0]["verified"])

  def test_basic_response(self):
    """Test basic response for a valid query."""
    assessment2_title = self.assessment2.title
    response = self._get_related_assessments(self.assessment1).json
    self.assertIn("total", response)
    self.assertIn("data", response)
    self.assertEqual(response["total"], 1)
    self.assertEqual(len(response["data"]), 1)
    self.assertEqual(response["data"][0]["title"], assessment2_title)

  @ddt.data(
      ({}, 2),
      ({"limit": "0,1"}, 2),
      ({"limit": "0,2"}, 2),
      ({"limit": "0,3"}, 2),
  )
  @ddt.unpack
  def test_total_count_with_ca(self, limit, expected_count):
    """Test total related assessments count for assessments with ca.

    The left outer join in our eager query on custom attribute values breaks
    the total count if on sa.func.count, but works if we use query.count()
    """
    cad = factories.CustomAttributeDefinitionFactory
    cads = [cad(definition_type="assessment") for _ in range(3)]

    for cad in cads:
      factories.CustomAttributeValueFactory(
          attributable=self.assessment1,
          custom_attribute=cad,
      )
      factories.CustomAttributeValueFactory(
          attributable=self.assessment2,
          custom_attribute=cad,
      )

    with mock.patch("ggrc.views.start_compute_attributes"):
      views.do_full_reindex()

    response = self._get_related_assessments(self.control, **limit).json
    self.assertEqual(response["total"], expected_count)

  @ddt.data(
      {},
      {"a": 55},
      {"object_type": "invalid", "object_id": 5},
      {"object_type": "Control", "object_id": "invalid"},
      {"object_type": "Control", "object_id": 5, "limit": "a,b"},
      {"object_type": "Control", "object_id": 5, "limit": "1"},
      {"object_type": "Control", "object_id": 5, "limit": "1,2,5"},
      {"object_type": "Control", "object_id": 5, "limit": "5,1"},
      {"object_type": "Control", "object_id": 5, "limit": "-5,-1"},
      {"object_type": "Control", "object_id": 5, "order_by": "not enough"},
  )
  def test_invalid_parameters(self, query_string):
    """Test invalid query parameters {0}."""
    self.assert400(self.client.get(self.URL_BASE, query_string=query_string))

  @ddt.data(
      ({}, 2),
      ({"limit": "0,1"}, 1),
      ({"limit": "1,2"}, 1),
      ({"limit": "1,3"}, 1),
      ({"limit": "0,2"}, 2),
      ({"limit": "0,7"}, 2),
  )
  @ddt.unpack
  def test_limit_clause(self, limit, expected_count):
    """Test limit clause for {0}."""
    response = self._get_related_assessments(self.control, **limit).json
    self.assertEqual(response["total"], 2)
    self.assertEqual(len(response["data"]), expected_count)

  @ddt.data(
      ({"order_by": "title,asc"}, ["A_1", "A_2"]),
      ({"order_by": "title,desc"}, ["A_2", "A_1"]),
      ({"order_by": "description,asc,title,asc"}, ["A_1", "A_2"]),
      ({"order_by": "description,desc,title,desc"}, ["A_2", "A_1"]),
  )
  @ddt.unpack
  def test_order_by_clause(self, order_by, titles_order):
    """Test order by for {0}."""
    response = self._get_related_assessments(self.control, **order_by).json
    titles = [assessment["title"] for assessment in response["data"]]
    self.assertEqual(titles, titles_order)

  def test_self_link(self):
    """Test that audits and assessments contain viewLink."""
    audit_self_link = u"/{}/{}".format(
        self.assessment2.audit._inflector.table_plural,
        self.assessment2.audit.id,
    )
    assessment_self_link = u"/{}/{}".format(
        self.assessment2._inflector.table_plural,
        self.assessment2.id,
    )
    response = self._get_related_assessments(self.assessment1).json
    self.assertIn("viewLink", response["data"][0]["audit"])
    self.assertIn("viewLink", response["data"][0])
    self.assertEqual(
        response["data"][0]["audit"]["viewLink"],
        audit_self_link,
    )
    self.assertEqual(
        response["data"][0]["viewLink"],
        assessment_self_link,
    )

  def test_cav(self):
    """Test that cav with type "Map:Person" contain attribute_object"""

    with factories.single_commit():
      person = factories.PersonFactory()
      person_id = person.id

      cad = factories.CustomAttributeDefinitionFactory(
          definition_type="assessment",
          attribute_type="Map:Person"
      )
      cav = factories.CustomAttributeValueFactory(
          custom_attribute=cad,
          attributable=self.assessment1,
          attribute_value="Person"
      )
      cav.attribute_object = person

    response = self._get_related_assessments(self.assessment2).json
    data_json = response["data"]

    self.assertEqual(len(data_json), 1)

    related_assessment_json = data_json[0]
    cavs_json = related_assessment_json["custom_attribute_values"]

    self.assertEqual(len(cavs_json), 1)

    cav_json = cavs_json[0]

    attribute_object_json = cav_json["attribute_object"]

    self.assertEqual(attribute_object_json, {
        u"type": u"Person",
        u"id": person_id
    })
