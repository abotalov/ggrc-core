# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Add risk propagation roles

Create Date: 2018-03-19 12:26:58.016090
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from ggrc.migrations.utils import acr_propagation

# revision identifiers, used by Alembic.
revision = '679480cbd712'
down_revision = '3e667570f21f'

_RISK_PROPAGATION = {
    acr_propagation.BASIC_ROLES: acr_propagation.PROPOSAL_RU,
}

PROPAGATION = {
    "Risk": _RISK_PROPAGATION,
}


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  acr_propagation.propagate_roles(PROPAGATION)


def downgrade():
  """Remove Risk propagated roles"""
  for object_type, roles_tree in PROPAGATION.items():
    acr_propagation.remove_propagated_roles(object_type, roles_tree.keys())
