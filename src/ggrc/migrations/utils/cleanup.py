# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Functions to remove references to obsolete entities from the DB."""

import sqlalchemy as sa

from alembic import op


def _make_single_column_table(table_name, column_name, column_type=sa.String):
  """Creates a SQLAlchemy representation for a single column in a table."""
  return sa.sql.table(
      table_name,
      sa.sql.column(column_name, column_type),
  )


def replace(alembic_op, table_name, field, old_value, new_value):
  """UPDATE :table_name SET :field = :new_value WHERE :field = :old_value."""
  tbl = _make_single_column_table(table_name, field)
  alembic_op.execute(
      tbl.update().values({
          tbl.c[field]: new_value,
      }).where(
          tbl.c[field] == old_value,
      )
  )


def delete(alembic_op, table_name, field, value):
  """DELETE FROM :table WHERE :field = :value."""
  tbl = _make_single_column_table(table_name, field)
  alembic_op.execute(
      tbl.delete().where(
          tbl.c[field] == value,
      ),
  )


def delete_old_roles(role_names):
  """Remove old roles from database."""

  roles = sa.sql.table(
      "roles",
      sa.sql.column('id', sa.Integer),
      sa.sql.column('name', sa.String),
  )

  user_roles = sa.sql.table(
      "user_roles",
      sa.sql.column('id', sa.Integer),
      sa.sql.column('role_id', sa.String),
  )

  obsolete_role_ids = sa.select([roles.c.id]).where(
      roles.c.name.in_(role_names),
  )

  op.execute(
      user_roles.delete().where(
          user_roles.c.role_id.in_(obsolete_role_ids)
      )
  )

  op.execute(
      roles.delete().where(
          roles.c.name.in_(role_names),
      )
  )
