# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Handlers for default people fields in assessment templates.

These should be used on default verifiers and default assignees.
"""

from ggrc.models import all_models
from ggrc.converters import errors
from ggrc.converters.handlers import handlers


class DefaultPersonColumnHandler(handlers.ColumnHandler):
  """Handler for default verifiers and assignees."""

  KEY_MAP = {
      "default_assignees": "assignees",
      "default_verifier": "verifiers",
  }

  PEOPLE_LABELS_MAP = {
      display_name.lower(): value
      for value, display_name
      in all_models.AssessmentTemplate.DEFAULT_PEOPLE_LABELS.items()
  }

  DEFAULT_EMPTY_VALUE = "--"

  def _parse_email_values(self):
    """Parse an email list of default assignees.

    This is the "other" option in the default assignee dropdown menu.
    """
    # This is not good and fast, because it executes query for each
    # field from each row that contains people list.
    # If the feature is used actively, it should be refactored
    # and optimized.
    new_objects = self.row_converter.block_converter.converter.new_objects
    new_people = new_objects[all_models.Person]

    people = []
    emails = []

    for email in self.raw_value.splitlines():
      email = email.strip()
      if not email:
        continue
      if email in new_people:
        # In "dry run" mode person.id is None, so it is replaced by int value
        # to pass validation.
        people.append(new_people[email].id or 0)
      else:
        emails.append(email)

    if emails:
      from ggrc.utils import user_generator
      for person in user_generator.find_users(emails):
        people.append(person.id)
        emails.remove(person.email)
      if emails:
        for email in emails:
          self.add_warning(errors.UNKNOWN_USER_WARNING,
                           column_name=self.display_name,
                           email=email)

    if not people and self.mandatory:
      self.add_error(errors.MISSING_VALUE_ERROR, column_name=self.display_name)
    return people

  def _parse_label_values(self):
    """Parse predefined default assignees.

    These values are the normal selection in the default assignees dropdown.
    """
    value = self.PEOPLE_LABELS_MAP.get(self.raw_value.lower())
    if not value and self.mandatory:
      self.add_error(errors.WRONG_REQUIRED_VALUE,
                     column_name=self.display_name,
                     value=self.raw_value.lower())
    return value

  def parse_item(self):
    """Parse values for default assignees."""
    if "@" in self.raw_value:
      return self._parse_email_values()
    else:
      return self._parse_label_values()

  def set_obj_attr(self):
    """Set default_assignees and default_verifiers attributes.

    Note that default_assignees and default_verifiers are not actual
    properties on the object that get stored. These are used as temporary
    placeholders and the property default_people, gets set using these
    two values, in check_assessment_template pre commit hook.
    """
    setattr(self.row_converter.obj, self.key, self.value)

  def get_value(self):
    """Get value from default_people attribute."""
    value = self.row_converter.obj.default_people.get(
        self.KEY_MAP[self.key],
        "ERROR",
    )

    if value is None:
      return self.DEFAULT_EMPTY_VALUE

    assessment_template = self.row_converter.obj
    default_people_labels = assessment_template.DEFAULT_PEOPLE_LABELS
    if isinstance(value, list):
      value = [default_people_labels.get(label, label) for label in value]
    else:
      value = default_people_labels.get(value, value)

    if isinstance(value, list):
      # This is not good and fast, because it executes query for each
      # field from each row that contains people list.
      # If the feature is used actively, it should be refactored
      # and optimized.
      people = all_models.Person.query.filter(
          all_models.Person.id.in_(value),
      ).all()
      value = "\n".join(p.email for p in people)
    return value
