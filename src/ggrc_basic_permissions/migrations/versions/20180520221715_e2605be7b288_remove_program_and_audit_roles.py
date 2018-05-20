# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
remove program and audit roles

Create Date: 2018-05-20 22:17:15.098031
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

from ggrc.migrations.utils import cleanup


# revision identifiers, used by Alembic.
revision = 'e2605be7b288'
down_revision = 'a90bda8e08ca'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  role_names = [
      'ProgramOwner',
      'ProgramEditor',
      'ProgramReader',
      'AuditorReader',
      'AuditorProgramReader',
      'ProgramAuditOwner',
      'ProgramAuditEditor',
      'ProgramAuditReader',
      'Auditor',
      'ProgramBasicReader',
      'ProgramMappingEditor',
  ]

  cleanup.delete_old_roles(role_names)


def downgrade():
  """Re-insert removed roles program and audit roles.

  This functian only takes care of inserting removed roles but not inserting
  user role entries, because we already have all roles handled by ACL.
  Adding the role entries back on downgrade should be done by the migration
  that moves the obsolete roles to ACL.

  For simplicity this migration only contains a section of a dump.

     mysqldump -hdb ggrcdev roles > roles.sql

  """

  op.execute(
      "INSERT INTO `roles` VALUES (1,'ProgramOwner','CODE DECLARED ROLE',"
      "'User with authorization to peform administrative tasks such as associ"
      "ating users to roles within the scope of of a program.<br/><br/>When a"
      " person creates a program they are automatically given the ProgramOwne"
      "r role. This allows them to Edit, Delete, or Map objects to the Progra"
      "m. It also allows them to add people and assign them roles when their "
      "programs are private. ProgramOwner is the most powerful role.',NULL,"
      "'2018-05-18 01:34:24','2018-05-18 01:34:24',NULL,'Private Program',1),"
      "(2,'ProgramEditor','CODE DECLARED ROLE','A user with authorization to "
      "edit mapping objects related to an access controlled program.<br/><br/"
      ">When a person has this role they can map and unmap objects to the Pro"
      "gram and edit the Program info, but they are unable to delete the Prog"
      "ram or assign other people roles for that program.',NULL,'2018-05-18 0"
      "1:34:24','2018-05-18 01:34:24',NULL,'Private Program',2),(3,'ProgramRe"
      "ader','CODE DECLARED ROLE','A user with authorization to read mapping "
      "objects related to an access controlled Program.<br/><br/>This is esse"
      "ntially a view only role. A person with this role can access and view "
      "an otherwise private program, but they cannot map to or edit that prog"
      "ram in any way.',NULL,'2018-05-18 01:34:24','2018-05-18 01:34:24',NULL"
      ",'Private Program',3),(9,'AuditorReader','CODE DECLARED ROLE','A user "
      "with Auditor role for a program audit will also have this role in the "
      "default object context so that the auditor will have access to the obj"
      "ects required to perform the audit.',NULL,'2018-05-18 01:34:24','2018-"
      "05-18 01:34:24',NULL,'System Implied',9),(10,'AuditorProgramReader','C"
      "ODE DECLARED ROLE','A user with Auditor role for a program audit will "
      "also have this role in the program context so that the auditor will ha"
      "ve access to the private program information and mappings required to "
      "perform the audit.',NULL,'2018-05-18 01:34:24','2018-05-18 01:34:24',N"
      "ULL,'Private Program Implied',10),(11,'ProgramAuditOwner','CODE DECLAR"
      "ED ROLE','A user with the ProgramOwner role for a private program will"
      " also have this role in the audit context for any audit created for th"
      "at program.',NULL,'2018-05-18 01:34:24','2018-05-18 01:34:24',NULL,'Au"
      "dit Implied',11),(12,'ProgramAuditEditor','CODE DECLARED ROLE','A user"
      " with the ProgramEditor role for a private program will also have this"
      " role in the audit context for any audit created for that program.',NU"
      "LL,'2018-05-18 01:34:24','2018-05-18 01:34:24',NULL,'Audit Implied',12"
      "),(13,'ProgramAuditReader','CODE DECLARED ROLE','A user with the Progr"
      "amReader role for a private program will also have this role in the au"
      "dit context for any audit created for that program.',NULL,'2018-05-18 "
      "01:34:24','2018-05-18 01:34:24',NULL,'Audit Implied',13),(14,'Auditor'"
      ",'CODE DECLARED ROLE','The permissions required by an auditor to acces"
      "s relevant resources for the program being audited.',NULL,'2018-05-18 "
      "01:34:24','2018-05-18 01:34:24',NULL,'Audit',14),(15,'ProgramBasicRead"
      "er','CODE DECLARED ROLE','Allow any user assigned a role in a program "
      "the ability to read Role resources.',1,'2018-05-18 01:34:24','2018-05-"
      "18 01:34:24',NULL,'Program Implied',15),(16,'ProgramMappingEditor','CO"
      "DE DECLARED ROLE','\n              This role grants a user permission "
      "to edit program mappings.\n              ',1,'2018-05-18 01:34:24','20"
      "18-05-18 01:34:24',NULL,'Private Program Implied',16),(17,'Creator','C"
      "ODE DECLARED ROLE','Global creator',NULL,'2018-05-18 01:34:24','2018-0"
      "5-18 01:34:24',NULL,'System',4)"
  )
