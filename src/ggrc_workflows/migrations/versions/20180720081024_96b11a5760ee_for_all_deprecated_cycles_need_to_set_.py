# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
For all deprecated cycles need to set is_active false if it doesn't is_done yet

Create Date: 2018-07-20 08:10:24.084605
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op


# revision identifiers, used by Alembic.
revision = '96b11a5760ee'
down_revision = '5eae0c070070'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  op.execute(
      "UPDATE cycles SET is_current = 0 WHERE "
      "status = 'Deprecated' AND is_current = 1")


def downgrade():
  """Downgrade database schema and/or data back to the previous revision.

  Upgrade is updating different sets of data, so, we can't revert it properly
  in downgrade and we just skip it.
  """
