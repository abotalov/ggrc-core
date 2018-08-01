# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Module contains Indexed mixin class"""
import itertools
from collections import namedtuple

from sqlalchemy import orm

from ggrc import db

from ggrc import fulltext


class ReindexRule(namedtuple("ReindexRule", ["model", "rule", "fields"])):
  """Class for keeping reindex rules"""
  __slots__ = ()

  def __new__(cls, model, rule, fields=None):
    return super(ReindexRule, cls).__new__(cls, model, rule, fields)


# pylint: disable=too-few-public-methods
class Indexed(object):
  """Mixin for Index And auto reindex current model instance.

  It should be last mixin in the scope if mixin that generate indexed query.
  """

  AUTO_REINDEX_RULES = [
      # Usage: ReindexRule("ModelName", lambda x: x.value)
  ]
  REQUIRED_GLOBAL_REINDEX = True

  PROPERTY_TEMPLATE = u"{}"

  def get_reindex_pair(self):
    return (self.__class__.__name__, self.id)

  @classmethod
  def get_insert_query_for(cls, ids):
    """Return insert class record query. It will return None, if it's empty."""
    if not ids:
      return None
    instances = cls.indexed_query().filter(cls.id.in_(ids))
    indexer = fulltext.get_indexer()
    rows = itertools.chain(*[indexer.records_generator(i) for i in instances])
    values = list(rows)
    if not values:
      return None
    return indexer.record_type.__table__.insert().values(values)

  @classmethod
  def get_delete_query_for(cls, ids):
    """Return delete class record query. If ids are empty, will return None."""
    if not ids:
      return None
    indexer = fulltext.get_indexer()
    return indexer.record_type.__table__.delete().where(
        indexer.record_type.type == cls.__name__
    ).where(
        indexer.record_type.key.in_(ids),
    )

  @classmethod
  def bulk_record_update_for(cls, ids):
    """Bulky update index records for current class"""
    delete_query = cls.get_delete_query_for(ids)
    insert_query = cls.get_insert_query_for(ids)
    for query in [delete_query, insert_query]:
      if query is not None:
        db.session.execute(query)

  @classmethod
  def indexed_query(cls):
    return cls.query.options(orm.Load(cls).load_only("id"),)
