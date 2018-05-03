# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Update document object

Create Date: 2018-04-12 13:19:09.278880
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "ee175ce1e775"
down_revision = "b1cb47a3bb3b"

TABLE = "documents"


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.add_column(TABLE,
                  sa.Column("slug", sa.String(length=250), nullable=False))
    op.add_column(TABLE,
                  sa.Column("status", sa.String(length=250), nullable=False,
                            server_default="Active"))
    op.add_column(TABLE,
                  sa.Column("recipients", sa.String(length=250),
                            nullable=True))
    op.add_column(TABLE,
                  sa.Column("send_by_default", sa.Boolean(), nullable=True))
    op.add_column(TABLE,
                  sa.Column("last_deprecated_date", sa.Date))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_column(TABLE, "slug")
    op.drop_column(TABLE, "status")
    op.drop_column(TABLE, "recipients")
    op.drop_column(TABLE, "send_by_default")
    op.drop_column(TABLE, "last_deprecated_date")

