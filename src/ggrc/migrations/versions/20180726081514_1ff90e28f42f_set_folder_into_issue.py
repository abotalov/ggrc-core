# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
set folder into issue

Create Date: 2018-07-26 08:15:14.349832
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '1ff90e28f42f'
down_revision = '2566da5aeca8'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  op.execute(
      "UPDATE issues "
      "JOIN audits on audits.id = issues.audit_id "
      "SET issues.folder = audits.folder;"
  )


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  pass
