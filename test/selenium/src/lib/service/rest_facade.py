# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""A facade for RestService.
Reasons for a facade:
* It is not very convenient to use
* More high level functions are often needed
"""
from lib.entities.entities_factory import AsmtTemplateManager

from lib import factory
from lib.constants import objects, roles
from lib.constants.element import AdminWidgetCustomAttributes
from lib.entities.entity import Representation
from lib.service import rest_service
from lib.utils.string_utils import StringMethods


def create_program(**attrs):
  """Create a program"""
  return rest_service.ProgramsService().create_obj(factory_params=attrs)


def create_objective(program=None, **attrs):
  """Create an objective (optionally map to a `program`)."""
  return _create_obj_in_program_scope("Objectives", program, **attrs)


def create_control(program=None, **attrs):
  """Create a control (optionally map to a `program`)"""
  return _create_obj_in_program_scope("Controls", program, **attrs)


def create_audit(program, **attrs):
  """Create an audit within a `program`"""
  return rest_service.AuditsService().create_obj(
      program=program.__dict__,
      factory_params=attrs)


def create_asmt(audit, **attrs):
  """Create an assessment within an audit `audit`"""
  attrs["audit"] = audit.__dict__
  return rest_service.AssessmentsService().create_obj(factory_params=attrs)


def create_asmt_template(audit, **attrs):
  """Create assessment template."""
  factory_params, attrs_remainder = _split_attrs(
      attrs, ['cad_type', 'dropdown_types_list'])
  attrs_remainder["audit"] = audit.__dict__
  cad = []
  if "custom_attribute_definitions" in attrs.keys():
    cad = attrs["custom_attribute_definitions"]
  elif "cad_type" in attrs.keys():
    cad = AsmtTemplateManager().generate_cads(**attrs_remainder)
  factory_params["custom_attribute_definitions"] = cad
  return rest_service.AssessmentTemplatesService().create_obj(
      factory_params=factory_params, **attrs_remainder)


def create_asmt_from_template(audit, asmt_template, control, **attrs):
  """Create an assessment from template
  :param control_snapshots: Should be list of control snapshots"""
  control_snapshots = [
      Representation.convert_repr_to_snapshot(objs=control, parent_obj=audit)]
  return rest_service.AssessmentsFromTemplateService().create_assessments(
      audit=audit, template=asmt_template, control_snapshots=control_snapshots,
      **attrs)[0]


def create_gcads(obj, **attrs):
  """Create global custom attribute definitions for all types"""
  gcas = []
  for gcas_type in AdminWidgetCustomAttributes.ALL_CA_TYPES:
    attrs['attribute_type'] = unicode(gcas_type)
    attrs['definition_type'] = unicode(objects.get_singular(obj))
    attrs['multi_choice_options'] = (
        StringMethods.random_list_strings()
        if gcas_type == AdminWidgetCustomAttributes.DROPDOWN
        else None)
    gcas.append(rest_service.CustomAttributeDefinitionsService().create_obj(
        obj_count=1, factory_params=attrs))
  return gcas


def create_issue(program=None):
  """Create a issue (optionally map to a `program`)"""
  issue = rest_service.IssuesService().create_obj()
  if program:
    map_objs(program, issue)
  return issue


def create_user():
  """Create a user"""
  return rest_service.PeopleService().create_obj()


def create_user_with_role(role_name):
  """Create user a role `role_name`"""
  user = create_user()
  role = next(role for role in roles.global_roles()
              if role["name"] == role_name)
  rest_service.UserRolesService().create_obj(person=user.__dict__, role=role)
  user.system_wide_role = role["name"]
  return user


def map_objs(src_obj, dest_obj):
  """Map two objects to each other"""
  rest_service.RelationshipsService().map_objs(
      src_obj=src_obj, dest_objs=dest_obj)


def get_obj(obj):
  """Get an object"""
  return rest_service.ObjectsInfoService().get_obj(obj)


def get_snapshot(obj, parent_obj):
  """Get (or create) a snapshot of `obj` in `parent_obj`"""
  return rest_service.ObjectsInfoService().get_snapshoted_obj(
      origin_obj=obj, paren_obj=parent_obj)


def map_to_snapshot(src_obj, obj, parent_obj):
  """Create a snapshot of `obj` in `parent_obj`.
  Then map `src_obj` to this snapshot.
  """
  snapshot = get_snapshot(obj, parent_obj)
  map_objs(src_obj, snapshot)


def _create_obj_in_program_scope(obj_name, program, **attrs):
  """Create an object with `attrs`.
  Optionally map this object to program.
  """
  factory_params, attrs_remainder = _split_attrs(attrs, ["program"])
  obj = factory.get_cls_rest_service(object_name=obj_name)().create_obj(
      factory_params=factory_params, **attrs_remainder)
  if program:
    map_objs(program, obj)
  return obj


def _split_attrs(attrs, keys_for_template=None):
  """Split `attrs` dictionary into two parts:
  * Dict with keys that are not in `keys_for_template`
  * Remainder dict with keys in `keys_for_template`
  """
  if keys_for_template is None:
    keys_for_template = []
  attrs_remainder = {}
  factory_params = {}
  for key, value in attrs.items():
    if key in keys_for_template:
      d = attrs_remainder
    else:
      d = factory_params
    d[key] = value
  return factory_params, attrs_remainder
