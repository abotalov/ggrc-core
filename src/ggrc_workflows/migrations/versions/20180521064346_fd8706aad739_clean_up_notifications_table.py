# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Clean up notifications table

Create Date: 2018-05-21 06:43:46.671332
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op


# revision identifiers, used by Alembic.
revision = 'fd8706aad739'
down_revision = '5206dc9f95f0'


def upgrade():
  """Remove invalid entries from notifications table.

  Notifications set the object id to 0 when the original object for the
  notification is deleted. The proper thing to do would be to delete those
  notifications which is now done by the orm relationship. This migration
  is just to clean up old data.

  This migration relies on the fact that all objects have a minimum id of 1.
  Only object with id 0 is an admin context which does not have notifications.
  This means it should be safe to remove notifications for objects with id 0.
  """
  op.execute("DELETE FROM notifications WHERE object_id = 0")


def downgrade():
  """Skip downgrade.

  Upgrade removes invalid data, so no action is needed in downgrade
  """
