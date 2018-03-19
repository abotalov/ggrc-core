# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
update acr table

Create Date: 2018-03-05 20:28:49.737209
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

from ggrc.migrations.utils import acr_propagation


# revision identifiers, used by Alembic.
revision = '3db5f2027c92'
down_revision = 'd1671a8dac7'

ASSESSMENT_ROLE_PROPAGATION = {
    "Relationship R": {
        "Audit R": {
            "Relationship R": {
                "Document R": {},
            },
        },
        "Document RU": {},
        "Comment R": {},
        "Issue R": {
            "Relationship R": {
                "Comment R": {},
                "Document R": {},
            },
        },
        "Snapshot R": {
            "Relationship R": {
                "Snapshot R": {},
            },
        },
    },
}


_BASIC_PROPAGATION = {
    "Admin": {
        "Relationship R": {
            "Comment R": {},
            "Document RU": {},
        },
    },
}

_PROPOSAL_PROPAGATION = {
    "Admin": {
        "Relationship R": {
            "Comment R": {},
            "Document RU": {},
            "Proposal RU": {},
        },
    },
}


PROPAGATION = {
    "Assessment": {
        ("Creators", "Assignees", "Verifiers"): ASSESSMENT_ROLE_PROPAGATION,
    },
    "AccessGroup": _BASIC_PROPAGATION,
    "Clause": _BASIC_PROPAGATION,
    "Contract": _BASIC_PROPAGATION,
    "Control": _PROPOSAL_PROPAGATION,
    "DataAsset": _BASIC_PROPAGATION,
    "Facility": _BASIC_PROPAGATION,
    "Issue": _BASIC_PROPAGATION,
    "Market": _BASIC_PROPAGATION,
    "Objective": _BASIC_PROPAGATION,
    "OrgGroup": _BASIC_PROPAGATION,
    "Policy": _BASIC_PROPAGATION,
    "Process": _BASIC_PROPAGATION,
    "Product": _BASIC_PROPAGATION,
    "Project": _BASIC_PROPAGATION,
    "Regulation": _BASIC_PROPAGATION,
    "Risk": _PROPOSAL_PROPAGATION,
    # "RiskAssessment": _BASIC_PROPAGATION,
    "Section": _BASIC_PROPAGATION,
    "Standard": _BASIC_PROPAGATION,
    "System": _BASIC_PROPAGATION,
    "Threat": _BASIC_PROPAGATION,
    "Vendor": _BASIC_PROPAGATION,
}


def _add_parent_id_column():
  op.add_column('access_control_roles', sa.Column(
      'parent_id', sa.Integer(), nullable=True))
  op.create_foreign_key(
      "fk_access_control_roles_parent_id",
      "access_control_roles", "access_control_roles",
      ["parent_id"], ["id"],
      ondelete="CASCADE"
  )


def _remove_parent_id_column():
  op.drop_constraint(
      "fk_access_control_roles_parent_id",
      "access_control_roles",
      "foreignkey",
  )
  op.drop_column('access_control_roles', 'parent_id')


def _add_assessment_roles_tree():
  acr_propagation.propagate_roles(PROPAGATION)


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  _add_parent_id_column()
  _add_assessment_roles_tree()


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  for object_type, roles_tree in PROPAGATION.items():
    acr_propagation.remove_propagated_roles(object_type, roles_tree.keys())
  _remove_parent_id_column()
