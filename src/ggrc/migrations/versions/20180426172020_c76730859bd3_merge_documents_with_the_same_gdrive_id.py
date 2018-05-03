# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Merge Documents with the same gdrive_id

Create Date: 2018-04-26 17:20:20.354276
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from ggrc.migrations import utils
from ggrc.migrations.utils import migrator

revision = 'c76730859bd3'
down_revision = 'ee175ce1e775'

TABLE = "documents"


def get_gdrive_id_to_migrate(connection):
  """Returns list gdrive is to process."""
  sql = """
      SELECT 
          d.gdrive_id
      FROM
          documents d
      WHERE d.kind='FILE' AND d.gdrive_id <> ''
      GROUP BY d.gdrive_id
      HAVING COUNT(d.gdrive_id) > 1
  """
  return connection.execute(text(sql)).fetchall()


def get_documents_to_merge(connection, gdrive_id):
  """Returns list of documents with the same gdrive_id."""
  sql = """
      SELECT DISTINCT
          res.id,
          res.modified_by_id,
          res.title,
          res.link,
          res.description,
          res.context_id,
          res.kind,
          res.source_gdrive_id,
          res.gdrive_id,
          res.slug,
          res.status,
          res.recipients,
          res.send_by_default,
          rel_id,
          counterparty_id,
          counterparty_type
      FROM
          (SELECT
              d.id,
              d.modified_by_id,
              d.title,
              d.link,
              d.description,
              d.context_id,
              d.kind,
              d.source_gdrive_id,
              d.gdrive_id,
              d.slug,
              d.status,
              d.recipients,
              d.send_by_default,
              r.id AS rel_id,
              r.destination_id AS counterparty_id,
              r.destination_type AS counterparty_type
          FROM
              documents d
          LEFT OUTER JOIN relationships r
              ON r.source_id = d.id
              AND r.source_type = 'Document'
          UNION ALL
          SELECT
              d.id,
              d.modified_by_id,
              d.title,
              d.link,
              d.description,
              d.context_id,
              d.kind,
              d.source_gdrive_id,
              d.gdrive_id,
              d.slug,
              d.status,
              d.recipients,
              d.send_by_default,
              r.id AS rel_id,
              r.source_id AS counterparty_id,
              r.source_type AS counterparty_type
          FROM
              documents d
          LEFT OUTER JOIN relationships r
              ON r.destination_id = d.id
              AND r.destination_type = 'Document') AS res
      WHERE
          res.gdrive_id = :gdrive_id
      ORDER BY res.id
  """
  return connection.execute(text(sql), gdrive_id=gdrive_id).fetchall()


def update_document_slug(connection, new_doc_id):
  """Update document slug"""
  sql = """
    UPDATE documents
    SET slug=CONCAT("DOCUMENT-",:id) 
    WHERE id=:id
  """
  connection.execute(text(sql), id=new_doc_id)


def copy_document(connection, old_doc):
  """Create copy of document object and return it's id"""
  sql = """
      INSERT INTO documents (
          modified_by_id,
          created_at,
          updated_at,
          title,
          link,
          description,
          context_id,
          kind,
          source_gdrive_id,
          gdrive_id,
          slug,
          status,
          recipients,
          send_by_default
          )
      VALUES (:modified_by_id, NOW(), NOW(), :title, :link,
              :description, :context_id, :kind,
              :source_gdrive_id, :gdrive_id, :slug, :status,
              :recipients, :send_by_default)
      """
  connection.execute(text(sql),
                     modified_by_id=old_doc.modified_by_id,
                     title=old_doc.title,
                     link=old_doc.link,
                     description=old_doc.description,
                     context_id=old_doc.context_id,
                     source_gdrive_id=old_doc.source_gdrive_id,
                     gdrive_id=old_doc.gdrive_id,
                     status=old_doc.status,
                     recipients=old_doc.recipients,
                     send_by_default=old_doc.send_by_default,
                     slug="TMP_SLUG",
                     kind="FILE")
  new_doc_id = utils.last_insert_id(connection)
  update_document_slug(connection, new_doc_id)
  utils.add_to_objects_without_revisions(connection, new_doc_id, "Document")

  return new_doc_id


def create_relationship(connection, source_id, source_type, doc_id):
  """Create relationship for new document"""
  inserted_id = None
  try:
    sql = """
        INSERT INTO relationships (
            source_id,
            source_type,
            destination_id,
            destination_type,
            created_at,
            updated_at,
            is_external)
        VALUES (:source_id, :source_type, :doc_id,
                'Document', NOW(), NOW(), '0');
    """
    connection.execute(text(sql),
                       source_id=source_id,
                       source_type=source_type,
                       doc_id=doc_id)
    inserted_id = utils.last_insert_id(connection)
    utils.add_to_objects_without_revisions(connection,
                                           inserted_id, "Relationship")
  except IntegrityError:
    print "Relationship between Document: {} and {}: {} exists already"\
      .format(doc_id, source_type, source_id)
  return inserted_id


def process_relationships(connection, document_data, doc_id):
  """Crates relationships between new doc and related objects, revisions"""
  for item in document_data:
    if item.counterparty_id:
      create_relationship(connection, item.counterparty_id,
                          item.counterparty_type, doc_id)
  old_relationship_ids = [d.rel_id for d in document_data if d.rel_id]
  delete_relationships(connection, old_relationship_ids)
  delete_revisions(connection, "Relationship", old_relationship_ids)


def delete_documents(connection, document_ids):
  """Delete old documents"""
  sql = """
      DELETE FROM documents WHERE id in :document_ids
  """
  connection.execute(text(sql), document_ids=document_ids)


def delete_relationships(connection, relationship_ids):
  """Delete old relationships"""
  if relationship_ids:
    sql = """
        DELETE FROM relationships WHERE id in :relationship_ids
    """
    connection.execute(text(sql), relationship_ids=relationship_ids)


def get_acls_to_merge(connection, document_ids):
  """Return acl list to merge"""
  sql = """
      SELECT 
          acl.id,
          acl.person_id,
          acl.ac_role_id,
          acl.object_id,
          acl.object_type,
          acl.modified_by_id,
          acl.context_id,
          acl.parent_id
      FROM access_control_list acl
        JOIN access_control_roles acr 
          ON acl.ac_role_id=acr.id 
      WHERE acr.name='Admin' 
        AND acr.object_type='Document' 
        AND acl.object_id IN :document_ids
  """
  return connection.execute(text(sql), document_ids=document_ids).fetchall()


def create_acl(connection, old_acl, new_doc_id):
  """Create new acl"""
  sql = """
      INSERT INTO access_control_list(
        person_id,
        ac_role_id,
        object_id,
        object_type,
        modified_by_id,
        context_id,
        updated_at,
        created_at)
      VALUES (:person_id, :ac_role_id, :object_id,
              :object_type, :modified_by_id, :context_id, NOW(), NOW());
  """
  connection.execute(text(sql),
                     person_id=old_acl.person_id,
                     ac_role_id=old_acl.ac_role_id,
                     object_id=new_doc_id,
                     object_type="Document",
                     modified_by_id=old_acl.modified_by_id,
                     context_id=old_acl.context_id
                     )
  acl_id = utils.last_insert_id(connection)
  utils.add_to_objects_without_revisions(connection,
                                         acl_id, "AccessControlList")


def delete_old_acls(connection, old_acl_ids):
  """Delete old acls"""
  if old_acl_ids:
    sql = """
      DELETE FROM access_control_list WHERE id in :old_acl_ids
    """
    connection.execute(text(sql), old_acl_ids=old_acl_ids)


def process_document_admin_acls(connection, document_ids, new_doc_id):
  """Find acl related to documents and update with new doc id"""
  acls_to_copy = get_acls_to_merge(connection, document_ids)
  for old_acl in acls_to_copy:
    create_acl(connection, old_acl, new_doc_id)
  old_acl_ids = [a.id for a in acls_to_copy]
  delete_old_acls(connection, old_acl_ids)
  delete_revisions(connection, "AccessControlList", old_acl_ids)


def delete_revisions(connection, resource_type, resource_ids):
  """Delete old revisions"""
  if resource_ids:
    sql = """
        DELETE FROM revisions WHERE resource_type=:resource_type 
          AND resource_id in :resource_ids
    """
    connection.execute(text(sql), resource_type=resource_type,
                       resource_ids=resource_ids)


def process_document(connection, document_data):
  """Process documents with the same gdive_id"""
  first_document_data = document_data[0]
  doc_id = copy_document(connection, first_document_data)
  document_ids = [d.id for d in document_data]
  process_document_admin_acls(connection, document_ids, doc_id)

  process_relationships(connection, document_data, doc_id)

  relationship_ids = [d.rel_id for d in document_data]
  delete_documents(connection, document_ids)
  delete_revisions(connection, "Document", document_ids)
  delete_relationships(connection, relationship_ids)


def add_indexes():
  """Add indexes to document table"""
  op.create_unique_constraint(constraint_name="idx_gdrive_id",
                              table_name=TABLE, columns=["gdrive_id"])
  op.create_unique_constraint(constraint_name="uq_control_document",
                              table_name=TABLE, columns=["slug"])


def run_migration():
  """Run main migration flow"""
  connection = op.get_bind()
  for gr in get_gdrive_id_to_migrate(connection):
    data = get_documents_to_merge(connection, gr.gdrive_id)
    if data:
      process_document(connection, data)
  migrate_url_to_reference_url(connection)
  #TODO: fix
  # add_indexes()


def migrate_url_to_reference_url(connection):
  """After the document epic document object should have 2 kinds

  REFERENCE_URL - for urls
  FILE - for gdrive files
  """
  migration_user_id = migrator.get_migration_user_id(connection)
  doc_ids = connection.execute(
    text("SELECT d.id FROM documents d WHERE d.kind='URL'")).fetchall()

  doc_ids = [d.id for d in doc_ids]
  utils.add_to_objects_without_revisions_bulk(connection, doc_ids, "Document")

  sql = """
      UPDATE documents SET
        kind='REFERENCE_URL',
        modified_by_id=:modified_by_id,
        updated_at=NOW()
      WHERE kind='URL'
  """
  connection.execute(text(sql),
                     modified_by_id=migration_user_id)

  connection.execute(text("""
      ALTER TABLE documents MODIFY
        kind enum('FILE','REFERENCE_URL') NOT NULL DEFAULT 'REFERENCE_URL';
  """))


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    run_migration()


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.drop_constraint("idx_gdrive_id", TABLE, "unique")
    op.drop_constraint("uq_control_document", TABLE, "unique")
    op.execute("""
      ALTER TABLE documents MODIFY
        kind enum('URL','FILE','REFERENCE_URL') NOT NULL DEFAULT 'URL';
  """)

