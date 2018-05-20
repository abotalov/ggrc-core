# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Remove legacy workflow roles

Create Date: 2018-05-20 04:32:24.347021
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

from ggrc.migrations.utils import cleanup


# revision identifiers, used by Alembic.
revision = 'aed91dd7ab9d'
down_revision = 'fd8706aad739'


def upgrade():
  """Remove obsolete workflow roles"""

  role_names = [
      'WorkflowOwner',
      'WorkflowMember',
      'BasicWorkflowReader',
      'WorkflowBasicReader',
      'WorkflowEditor',
  ]

  cleanup.delete_old_roles(role_names)


def downgrade():
  """Re-insert removed roles.

  This functian only takes care of inserting removed roles but not inserting
  user role entries, because we already have all roles handled by ACL.
  Adding the role entries back on downgrade should be done by the migration
  that moves the obsolete roles to ACL.

  For simplicity this migration only contains a section of a dump.

     mysqldump -hdb ggrcdev roles > roles.sql

  """

  op.execute("""
  INSERT INTO `roles` VALUES (
    18,
    'WorkflowOwner',
    'CODE DECLARED ROLE',
    'This role grants a user permission to edit workflow mappings and details',
    1,
    '2018-05-20 04:21:07',
    '2018-05-20 04:21:07',
    NULL,
    'Workflow',
    NULL
  ),(
    19,
    'WorkflowMember',
    'CODE DECLARED ROLE',
    'This role grants a user permission to edit workflow mappings',
    1,
    '2018-05-20 04:21:07',
    '2018-05-20 04:21:07',
    NULL,
    'Workflow',
    NULL
  ),(
    20,
    'BasicWorkflowReader',
    'CODE DECLARED ROLE',
    ' ',
    1,
    '2018-05-20 04:21:07',
    '2018-05-20 04:21:07',
    NULL,
    'Workflow Implied',
    NULL
  ),(
    21,
    'WorkflowBasicReader',
    'CODE DECLARED ROLE',
    ' ',
    1,
    '2018-05-20 04:21:07',
    '2018-05-20 04:21:07',
    NULL,
    'Workflow Implied',
    NULL
  ),(
    22,
    'WorkflowEditor',
    'CODE DECLARED ROLE',
    'This role grants a user permission to edit workflow mappings and details',
    NULL,
    '2018-05-20 04:21:09',
    '2018-05-20 04:21:09',
    NULL,
    'Workflow Implied',
    NULL
  )
  """)
