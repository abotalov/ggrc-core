# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Checker function for import pre commit hooks."""

from ggrc.converters import errors


def check_tasks(row_converter):
  """Checker for task group task objects.

  This checker should make sure if a task group task has any invalid values
  that should be ignored. Object will not be checked if there's already
  an error on and it's marked as ignored.

  Args:
    row_converter: RowConverter object with row data for a task group task
      import.
  """
  if row_converter.ignore:
    return

  obj = row_converter.obj
  if obj.start_date > obj.end_date:
    row_converter.add_error(
        errors.INVALID_START_END_DATES,
        start_date="Start date",
        end_date="End date",
    )


DENY_FINISHED_DATES_STATUSES_STR = ("<'Assigned' / 'In Progress' / "
                                    "'Declined' / 'Deprecated'>")
DENY_VERIFIED_DATES_STATUSES_STR = ("<'Assigned' / 'In Progress' / "
                                    "'Declined' / 'Deprecated' / 'Finished'>")


def check_cycle_tasks(row_converter):  # noqa
  """Checker for CycleTaskGroupObjectTask model objects.

  This checker should make sure if a cycle-task has any invalid values
  that should be ignored during update via import.

  Args:
    row_converter: RowConverter object with row data for a cycle-task
      import.
  """
  # Cycle-Task creation is denied. Don't need checks for new items.
  if row_converter.is_new:
    return
  obj = row_converter.obj
  if obj.start_date > obj.end_date:
    row_converter.add_error(
        errors.INVALID_START_END_DATES,
        start_date="Start Date",
        end_date="Due Date",
    )
  if (obj.finished_date and obj.verified_date and
          obj.finished_date > obj.verified_date):
    row_converter.add_error(
        errors.INVALID_START_END_DATES,
        start_date="Actual Finish Date",
        end_date="Actual Verified Date",
    )
  if obj.status not in (obj.FINISHED, obj.VERIFIED):
    if obj.finished_date:
      row_converter.add_error(
          errors.INVALID_STATUS_DATE_CORRELATION,
          date="Actual Finish Date",
          deny_states=DENY_FINISHED_DATES_STATUSES_STR,
      )
    if obj.verified_date:
      row_converter.add_error(
          errors.INVALID_STATUS_DATE_CORRELATION,
          date="Actual Verified Date",
          deny_states=DENY_VERIFIED_DATES_STATUSES_STR,
      )
  if obj.status == obj.FINISHED and obj.verified_date:
    row_converter.add_error(
        errors.INVALID_STATUS_DATE_CORRELATION,
        date="Actual Verified Date",
        deny_states=DENY_VERIFIED_DATES_STATUSES_STR,
    )


def check_workflows(row_converter):
  """Checker for Workflow object.

  Check if a Workflow has any invalid values. If so, it should be ignored.
  Object will not be checked if there's already an error exists
  and it's marked as ignored.

  Args:
    row_converter: RowConverter object with row data for a task group task
      import.
  """
  if row_converter.ignore:
    return

  obj = row_converter.obj
  if (obj.unit is None and obj.repeat_every is not None or
          obj.unit is not None and obj.repeat_every is None):
    row_converter.add_error(
        errors.VALIDATION_ERROR,
        column_name="'repeat_every', 'unit'",
        message="'repeat_every' and 'unit' fields can be set to NULL only"
                " simultaneously",
    )


def check_assessment(row_converter):
  """Checker for Assessment model instance.

  This checker should make sure if an assessment are invalid or non-importable
  and should be ignored.

  Args:
      row_converter: RowConverter object with row data for an assessment
        import.
      kwargs: Dict with options.
  """
  if row_converter.obj.archived:
    row_converter.add_error(errors.ARCHIVED_IMPORT_ERROR)


def check_assessment_template(row_converter):
  """Checker for AssessmentTemplate model objects.

  This checker sets default_people attribute from values of default_assignees
  and default_verifier.

  Args:
     row_converter: RowConverter object with row data for a cycle-task
     import.
  """
  if row_converter.ignore:
    return

  key_map = {
      "default_assignees": "assignees",
      "default_verifier": "verifiers",
  }
  key_map_inverse = {
      "assignees": "default_assignees",
      "verifiers": "default_verifier",
  }
  default_empty_value = "--"

  default_people = {}
  for key, value in key_map.iteritems():
    default_people[value] = getattr(row_converter.obj, key, "")

  if not row_converter.obj.default_people:
    row_converter.obj.default_people = default_people
    return

  for key, value in default_people.iteritems():
    header = row_converter.headers.get(key_map_inverse[key], None)
    previous_value = row_converter.obj.default_people.get(key, "")
    if not header:
      default_people[key] = previous_value
      continue

    index = row_converter.headers.keys().index(key_map_inverse[key])
    raw_value = row_converter.row[index]

    if raw_value == default_empty_value:
      default_people[key] = None
    elif not value:
      default_people[key] = None if row_converter.is_new else previous_value

  row_converter.obj.default_people = default_people


CHECKS = {
    "TaskGroupTask": check_tasks,
    "CycleTaskGroupObjectTask": check_cycle_tasks,
    "Workflow": check_workflows,
    "Assessment": check_assessment,
    "AssessmentTemplate": check_assessment_template,
}
