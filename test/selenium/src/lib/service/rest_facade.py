# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""A facade for RestService.
Reasons for a facade:
* It is not very convenient to use
* More high level functions are often needed
"""
import requests

from lib.constants import roles, objects
from lib.service import rest_service
from lib.service.rest.client import RestClient
from lib.service.rest_service import BaseRestService


def create_program():
  """Create a program"""
  return rest_service.ProgramsService().create_obj()


def create_objective(program=None):
  """Create an objecive (optionally map to a `program`)."""
  objective = rest_service.ObjectivesService().create_obj()
  if program:
    map_objs(program, objective)
  return objective


def create_control(program=None):
  """Create a control (optionally map to a `program`)"""
  control = rest_service.ControlsService().create_obj()
  if program:
    map_objs(program, control)
  return control


def create_audit(program):
  """Create an audit within a `program`"""
  return rest_service.AuditsService().create_obj(program=program.__dict__)


def create_assessment(audit, **attrs):
  """Create an assessment within an audit `audit`"""
  attrs["audit"] = audit.__dict__
  return rest_service.AssessmentsService().create_obj(**attrs)


def create_user_with_role(role_name):
  user = rest_service.PeopleService().create_obj()
  role = next(role for role in roles.Roles().roles()
              if role["name"] == role_name)
  rest_service.UserRolesService().create_obj(person=user.__dict__, role=role)
  return user


def map_objs(src_obj, dest_obj):
  """Map two objects to each other"""
  rest_service.RelationshipsService().map_objs(
      src_obj=src_obj, dest_objs=dest_obj)


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


def can_view(obj):
  response = RestClient("").get_object(obj.href)
  return response.status_code == requests.codes.ok and response.json().itervalues().next()["title"] == obj.title
