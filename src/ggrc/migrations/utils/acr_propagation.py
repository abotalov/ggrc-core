# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module with helpers for creating propagation access control roles."""

import datetime

import sqlalchemy as sa

from alembic import op

BASIC_ROLES = (
    "Admin",
    "Primary Contacts",
    "Secondary Contacts",
)

BASIC_PROPAGATION = {
    "Admin": {
        "Relationship R": {
            "Comment R": {},
            "Document RU": {},
        },
    },
}

_PROPOSAL_PROPAGATION = {
    "Relationship R": {
        "Comment R": {},
        "Document RU": {},
        "Proposal RU": {},
    },
}


acr = sa.sql.table(
    "access_control_roles",
    sa.sql.column('id', sa.Integer),
    sa.sql.column('name', sa.String),
    sa.sql.column('object_type', sa.String),
    sa.sql.column('tooltip', sa.String),
    sa.sql.column('read', sa.Boolean),
    sa.sql.column('update', sa.Boolean),
    sa.sql.column('delete', sa.Boolean),
    sa.sql.column('my_work', sa.Boolean),
    sa.sql.column('created_at', sa.DateTime),
    sa.sql.column('modified_by_id', sa.Integer),
    sa.sql.column('updated_at', sa.DateTime),
    sa.sql.column('context_id', sa.Integer),
    sa.sql.column('internal', sa.Integer),
    sa.sql.column('non_editable', sa.Boolean),
    sa.sql.column('notify_about_proposal', sa.Integer),
    sa.sql.column('parent_id', sa.Integer),
)


def _parse_object_data(object_data):
  """Parse object data for role propagation.

  Examples:
    "Comment RU" > "Comment", {"read": True, "update": True, "delete": False}
    "Assessment" > "Assessment", {}

  Args:
    object_data: String containing object_type and permission data

  Returns:
    string for object type and dictionary for permissions data.
  """
  permissions_map = {
      "read": "R",
      "update": "U",
      "delete": "D",
  }
  permissions = {}
  data = object_data.split()
  if len(data) == 2:
    for key, flag in permissions_map.items():
      permissions[key] = flag in data[1]

  return data[0], permissions


def _add_subtree(tree, role_name, parent_id):
  """Add propagated roles for the given tree.

  keys of the tree must contain object data in form of "object_type RUD"
  strings or a list of those strings.
  """
  connection = op.get_bind()
  role_name = "{}*{}*".format(role_name.rstrip("*"), parent_id)
  for object_data_list, subtree in tree.items():
    if isinstance(object_data_list, basestring):
      object_data_list = [object_data_list]
    for object_data in object_data_list:
      object_type, permissions_dict = _parse_object_data(object_data)
      insert = connection.execute(
          acr.insert().values(
              name=role_name,
              object_type=object_type,
              parent_id=parent_id,
              created_at=datetime.datetime.now(),
              updated_at=datetime.datetime.now(),
              internal=True,
              non_editable=True,
              **permissions_dict
          )
      )
      _add_subtree(subtree, role_name, insert.lastrowid)


def _get_acr(object_type, name):
  """Get access control entry for a given role on object."""
  connection = op.get_bind()
  return connection.execute(
      acr.select().where(
          sa.and_(
              acr.c.name == name,
              acr.c.object_type == object_type,
          )
      )
  ).fetchone()


def _propagate_object_roles(object_type, roles_tree):
  """Propagate roles in the role tree for a given object type.

  The role propagation rules are given in the following format:
  {
      <role_name> | <iterable role_names>: {
          "<sub_type> <rights>": {
              "<sub_type> <rights>": {
                  ...
              },
          },
          ...
      }
  }

  Where:
    <sub_type> is a class name of a directly linked object for the object_type.
    <rights> is a subset of RUD representing flags for read update and delete.

  Args:
    object_type: Class name of the object for which we want to propagate roles.
    roles_tree: a dictionary with the role propagation rules.
  """
  for role_names, propagation_tree in roles_tree.items():
    if isinstance(role_names, basestring):
      role_names = [role_names]

    for role_name in role_names:
      role = _get_acr(object_type, role_name)
      _add_subtree(propagation_tree, role.name, role.id)


def propagate_roles(propagation_rules):
  for object_type, roles_tree in propagation_rules.items():
    _propagate_object_roles(object_type, roles_tree)


def remove_propagated_roles(object_type, role_names):
  """Remove propagated roles.

  Args:
    object_type: type of object for role deletion.
    role_names: list of role names for the given object type whose propagations
      we wish to delete.
  """
  connection = op.get_bind()
  parent_ids = connection.execute(
      acr.select([acr.parent_id]).where(
          sa.and_(
              acr.c.name.in_(role_names),
              acr.c.object_type == object_type,
          )
      )
  ).fetchall()
  ids = [row.parent_id for row in parent_ids]
  op.execute(
      acr.delete().where(
          acr.c.parent_id.in_(ids)
      )
  )
