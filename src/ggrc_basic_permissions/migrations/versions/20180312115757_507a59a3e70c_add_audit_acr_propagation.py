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

_AUDIT_FULL_ACCESS = {
    "Relationship R": {
        "Assessment RUD": {
            "Relationship R": {
                "Comment R": {},
                "Document RU": {},
            },
        },
        "AssessmentTemplate RUD": {},
        "Document RU": {},
        "Issue RUD": {
            "Relationship R": {
                "Comment R": {},
                "Document RU": {},
            },
        },
    },
    "Snapshot RU": {},
}

_AUDIT_READ_ACCESS = {
    "Relationship R": {
        "Assessment RU": {
            "Relationship R": {
                "Comment R": {},
                "Document RU": {},
            },
        },
        "AssessmentTemplate R": {},
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


_PROGRAM_OBJECTS = (
    "AccessGroup",
    "Clause",
    "Contract",
    # "Control",  # control is separate due to proposals
    "DataAsset",
    "Facility",
    "Issue",
    "Market",
    "Objective",
    "OrgGroup",
    "Policy",
    "Process",
    "Product",
    "Project",
    "Regulation",
    # "Risk",  # excluded due to proposals
    "RiskAssessment",
    "Section",
    "Standard",
    "System",
    "Threat",
    "Vendor",
)

PROPAGATION = {
    "Program": {
        ("Program Managers", "Program Editors"): {
            "Audit RUD": _AUDIT_FULL_ACCESS,
            "Relationship R": {
                "Comment R": {},
                "Document RU": {},
                _PROGRAM_OBJECTS: {
                    "Relationship R": {
                        "Comment R": {},
                        "Document RU": {},
                    }
                },
                ("Control", "Risk"): {
                    "Relationship R": {
                        "Comment R": {},
                        "Document RU": {},
                        "Proposal RU": {},
                    }
                },
            }
        },
        "Program Readers": {
            "Audit R": _AUDIT_READ_ACCESS,
            "Relationship R": {
                "Comment R": {},
                "Document R": {},
                _PROGRAM_OBJECTS: {
                    "Relationship R": {
                        "Comment R": {},
                        "Document R": {},
                    }
                },
                ("Control", "Risk"): {
                    "Relationship R": {
                        "Comment R": {},
                        "Document R": {},
                        "Proposal R": {},
                    }
                },
            }
        },
    },
    "Audit": {
        # Audit captains might also need to get propagated access to program
        # and all program related objects, so that they could clone audits and
        # update all audit snapshots.
        "Audit Captains": _AUDIT_FULL_ACCESS,
        "Auditors": _AUDIT_READ_ACCESS,
    },
}


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  acr_propagation.propagate_roles(PROPAGATION)


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  for object_type, roles_tree in PROPAGATION.items():
    acr_propagation.remove_propagated_roles(object_type, roles_tree.keys())
