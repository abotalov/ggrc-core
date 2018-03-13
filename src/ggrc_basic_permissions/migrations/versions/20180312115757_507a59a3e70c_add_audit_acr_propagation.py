# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
update acr table

Create Date: 2018-03-05 20:28:49.737209

"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name


from ggrc.migrations.utils import acr_propagation

# revision identifiers, used by Alembic.
revision = '3db5f2027c92'
down_revision = '242b8dc8493b'


AUDIT_PROPAGATION = {
    "Audit Captains": {
        "Relationship R": {
            "Assessment RUD": {
                "Relationship R": {
                    "Comment R": {},
                    "Document RU": {},
                },
            },
            "AssessmentTemplate RUD": {},
            "Comment R": {},
            "Document RU": {},
            "Issue RUD": {
                "Relationship R": {
                    "Comment R": {},
                    "Document RU": {},
                },
            },
        },
        "Snapshot RU": {},
    },
    "Auditors": {
        "Relationship R": {
            "Assessment RU": {
                "Relationship R": {
                    "Comment R": {},
                    "Document RU": {},
                },
            },
            "AssessmentTemplate R": {},
            "Comment R": {},
            "Document R": {},
            "Issue RU": {
                "Relationship R": {
                    "Comment R": {},
                    "Document RU": {},
                },
            },
        },
        "Snapshot RU": {},
    }
}


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  acr_propagation.propagate_roles("Audit", AUDIT_PROPAGATION)


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  acr_propagation.remove_propagated_roles("Audit", AUDIT_PROPAGATION.keys())
