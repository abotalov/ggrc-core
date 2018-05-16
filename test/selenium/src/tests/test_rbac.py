# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Tests for RBAC"""
import sys

import inflection
import pytest

from lib import base, environment
from lib.constants import roles, users
from lib.entities.entities_factory import EntitiesFactory
from lib.service import rest_facade, webui_facade
from lib.service.rest.client import RestClient


class Entity(object):
  def __init__(self, **attrs):
    super(Entity, self).__init__()
    self._set_default_values()
    for attr_name in attrs.keys():
      setattr(self, attr_name, attrs[attr_name])

  def _set_default_values(self):
    self.context = None
    type = self.__class__.__name__.replace("Entity", "")
    self.title = EntitiesFactory.generate_string(type)


class ProgramEntity(Entity):
  def _set_default_values(self):
    super(ProgramEntity, self)._set_default_values()
    self.program_managers = [users.get_current_user()]


class AuditEntity(Entity):
  def _set_default_values(self):
    super(AuditEntity, self)._set_default_values()
    self.audit_captains = [users.get_current_user()]


class RestCreation(object):
  API = "api"

  def create_obj(self, **attrs):
    url = "".join([environment.app_url, self.API, "/",
                   self._pluralized_underscored_type()])
    payload = [{self._underscored_type(): self._rest_dict(**attrs)}]
    response = RestClient("").send_post(url=url, json=payload)
    rest_dict = self._get_obj_from_response(response)
    return self._entity_cls()(**rest_dict)

  def _type(self):
    return self.__class__.__name__.replace("RestCreation", "")

  def _underscored_type(self):
    return inflection.underscore(self._type())

  def _pluralized_underscored_type(self):
    return inflection.pluralize(self._underscored_type())

  def _entity_cls(self):
    cls_name = "{}Entity".format(self._type())
    return getattr(sys.modules[__name__], cls_name)

  def _rest_entity_cls(self):
    cls_name = "{}RestEntity".format(self._type())
    return getattr(sys.modules[__name__], cls_name)

  def _rest_dict(self, **attrs):
    entity = self._entity_cls()(**attrs)
    rest_entity = self._rest_entity_cls()(entity)
    return rest_entity.__dict__

  # def _restify_obj(self, entity):
  #   dictionary = entity.__dict__
  #   return {key: self._restify_field(key, dictionary[key])
  #           for key in self._rest_fields()}

  # def _restify_field(self, key, value):
  #   method_name = "{}_field".format(key)
  #   if hasattr(self, method_name):
  #     return getattr(self, method_name, value)(value)
  #   else:
  #     return value

  # def _rest_fields(self):
  #   raise NotImplementedError

  def _get_obj_from_response(self, response):
    assert response[0][0] == 201
    assert response[0][1].keys() == [self._underscored_type()]
    return response[0][1][self._underscored_type()]


class RestEntity(object):
  def __init__(self):
    super(RestEntity, self).__init__()
    entity_dict = entity.__dict__
    for attr_name in self._rest_fields():
      value = None
      method_name = "{}_from_entity".format(attr_name)
      if hasattr(self, method_name):
        value = getattr(self, method_name)(entity)
      elif attr_name in entity_dict:
        value = entity_dict[attr_name]
      setattr(self, attr_name, value)

  @classmethod
  def from_entity(cls, entity):
    rest_entity = cls()
    for attr_name in rest_entity._rest_fields():
      value = None
      method_name = "{}_from_entity".format(attr_name)
      if hasattr(self, method_name):
        value = getattr(self, method_name)(entity)
      elif attr_name in entity_dict:
        value = entity_dict[attr_name]
      setattr(self, attr_name, value)

  def _rest_fields(self):
    raise NotImplementedError

  def _type(self):
    return self.__class__.__name__.replace("RestEntity", "")

  def _part_of_dict(self, dictionary, keys):
    return {key: dictionary[key] for key in keys if key in dictionary}

  def _to_acl(self, entity_obj, attrs):
    access_control_list = []
    for attr in attrs:
      if hasattr(entity_obj, attr):
        people = getattr(entity_obj, attr)
        acr_name = inflection.titleize(attr)
        for person in people:
          access_control_list.append(self._acl_dict(acr_name, person))
    return access_control_list

  def _acl_dict(self, role_name, person):
    return {
      "ac_role_id": roles.ACLRolesIDs.id_of_role(object_type=self._type(),
                                                 name=role_name),
      "person": person.repr_min_dict()
    }


class ProgramRestEntity(RestEntity):
  def _rest_fields(self):
    return ["access_control_list", "context", "custom_attribute_definitions",
            "custom_attribute_values", "description", "kind", "notes",
            "recipients", "send_by_default", "slug", "status", "title"]

  def access_control_list_from_entity(self, entity_obj):
    return self._to_acl(entity_obj, ["primary_contacts", "program_managers",
                                     "program_editors", "program_readers"])


class AuditRestEntity(RestEntity):
  def _rest_fields(self):
    return ["access_control_list", "audit_firm", "can_use_issue_tracker",
            "context",
            "custom_attribute_definitions", "custom_attribute_values",
            "description", "end_date", "issue_tracker", "modified_by_id",
            "program", "report_end_date", "report_start_date", "slug",
            "start_date", "status", "title"]

  def access_control_list_from_entity(self, entity_obj):
    return self._to_acl(entity_obj, ["audit_captains", "auditors"])

  def program_from_entity(self, entity_obj):
    return self._part_of_dict(entity_obj.program.__dict__, ["href", "id", "type"])


class ProgramRestCreation(RestCreation):
  pass


class AuditRestCreation(RestCreation):
  pass


# class ProgramRestCreation(RestCreation):
#   def _rest_fields(self):
#     return ["access_control_list", "context", "custom_attribute_definitions",
#             "custom_attribute_values", "description", "kind", "notes",
#             "recipients", "send_by_default", "slug", "status", "title"]
#
#
# class AuditRestCreation(RestCreation):
#   def _rest_fields(self):
#     return ["access_control_list", "audit_firm", "can_use_issue_tracker",
#             "context",
#             "custom_attribute_definitions", "custom_attribute_values",
#             "description", "end_date", "issue_tracker", "modified_by_id",
#             "program", "report_end_date", "report_start_date", "slug",
#             "start_date", "status", "title"]
#
#   def access_control_list_field(self):
#     return self._to_acl("audit_captains", "auditors")
#
#   def program_field(self, field):
#     return self._part_of_dict(field.__dict__, ["href", "id", "type"])


def create_program(**attrs):
  return ProgramRestCreation().create_obj(**attrs)


def create_audit(program, **attrs):
  attrs["program"] = program
  return AuditRestCreation().create_obj(**attrs)


class TestRBAC(base.Test):
  ALL_ROLES = [roles.CREATOR, roles.READER, roles.EDITOR, roles.ADMINISTRATOR]

  @pytest.fixture()
  def users_with_all_roles(self):
    return {role: rest_facade.create_user_with_role(role_name=role)
            for role in self.ALL_ROLES}

  @pytest.mark.parametrize(
    "role",
    [roles.CREATOR, roles.READER, roles.EDITOR]
  )
  def test_object_creation(self, role, selenium):
    user = rest_facade.create_user_with_role(role_name=role)
    users.set_current_user(user)
    objs = [rest_facade.create_program(), rest_facade.create_control()]
    for obj in objs:
      webui_facade.assert_can_edit(selenium, obj, can_edit=True)
      webui_facade.assert_can_delete(selenium, obj, can_delete=True)

  @pytest.mark.parametrize(
    "login_role, can_view, can_edit",
    [
      (roles.CREATOR, False, False),
      (roles.READER, True, False),
      (roles.EDITOR, True, True)
    ]
  )
  def test_permissions(
    self, users_with_all_roles, login_role, can_view, can_edit, selenium
  ):
    objs = []
    roles = [role for role in self.ALL_ROLES if role != login_role]
    for role in roles:
      users.set_current_user(users_with_all_roles[role])
      program = rest_facade.create_program()
      control = rest_facade.create_control(program)
      objs.extend([program, control])
    users.set_current_user(users_with_all_roles[login_role])
    for obj in objs:
      webui_facade.assert_can_view(selenium, obj, can_view=can_view)
      if can_view:
        webui_facade.assert_can_edit(selenium, obj, can_edit=can_edit)
        webui_facade.assert_can_delete(selenium, obj, can_delete=can_edit)

  def test_1(self, selenium):
    editor = rest_facade.create_user_with_role(roles.EDITOR)
    creator = rest_facade.create_user_with_role(roles.CREATOR)
    users.set_current_user(editor)
    program = rest_facade.create_program()
    control = rest_facade.create_control(program=program)
    audit = rest_facade.create_audit(program, auditors=[creator])
    #webui_facade.assert_can_view(selenium, audit, can_view=True)
    users.set_current_user(creator)
    #webui_facade.assert_can_view(selenium, audit, can_view=True)
    webui_facade.assert_can_edit(selenium, audit, can_edit=False)
    webui_facade.assert_can_edit(selenium, control, can_edit=False)

  def test_2(self):
    editor = rest_facade.create_user_with_role(roles.EDITOR)
    creator = rest_facade.create_user_with_role(roles.CREATOR)
    users.set_current_user(editor)
    program = create_program()
    audit = create_audit(program, auditors=[creator])
    #control = rest_facade.create_control(program=program)
