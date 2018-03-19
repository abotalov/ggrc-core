# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Add workflow propagation roles

Create Date: 2018-03-19 11:51:08.836803
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from ggrc.migrations.utils import acr_propagation

# revision identifiers, used by Alembic.
revision = '1af8cf55ae02'
down_revision = '4489d0ec0076'


PROPAGATION = {
    "Workflow": {
        "Workflow Member": {
            "TaskGroup R": {
                "TaskGroupTask R": {},
                "TaskGroupObject R": {},
            },
            "Cycle R": {
                "CycleTaskGroup R": {
                    "CycleTaskGroupObjectTask R": {
                        "CycleTaskEntry R": {},
                    },
                },
            },
        },
        "Admin": {
            "TaskGroup RUD": {
                "TaskGroupTask RUD": {},
                "TaskGroupObject RUD": {},
            },
            "Cycle RUD": {
                "CycleTaskGroup RUD": {
                    "CycleTaskGroupObjectTask RUD": {
                        "CycleTaskEntry RUD": {},
                    },
                },
            },
        },
    },
}


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  acr_propagation.propagate_roles(PROPAGATION)


def downgrade():
  """Remove Risk propagated roles"""
  for object_type, roles_tree in PROPAGATION.items():
    acr_propagation.remove_propagated_roles(object_type, roles_tree.keys())
