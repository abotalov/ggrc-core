# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Memcache implements the remote AppEngine Memcache mechanism."""

from collections import OrderedDict
from copy import deepcopy

import flask
from google.appengine.api import memcache

from ggrc import settings
from ggrc.cache import cache


class MemCache(cache.Cache):
  """MemCache class."""

  def __init__(self):
    super(MemCache, self).__init__()
    self.name = 'memcache'
    self.client = None

    self.memcache_client = memcache.Client()

    self.supported_resources.update({
        cache_entry.model_plural: cache_entry.class_name
        for cache_entry in cache.all_cache_entries()
        if cache_entry.cache_type is self.name})

  def get_name(self):
    return self.name

  def get(self, category, resource, filter):
    """ get items from mem cache for specified filter

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      filter: dictionary containing ids and optional attrs

    Returns:
      All or None policy is applied by default
      None on any errors
      otherwise returns JSON string representation
    """

    if not self.is_caching_supported(category, resource):
      return None
    # TODO(dan): use memcache.Client.get_multi() instead of gets()
    #
    data = OrderedDict()
    cache_key = self.get_key(category, resource)
    if cache_key is None:
      return None
    ids, attrs = self.parse_filter(filter)
    if ids is None and attrs is None:
      return None
    else:
      if ids is None:
        return None
    for id_ in ids:
      attrvalues = self.memcache_client.gets(cache_key + ":" + str(id_))
      if attrvalues is not None:
        if attrs is None:
          data[id_] = attrvalues
        else:
          attr_dict = OrderedDict()
          for attr in attrs:
            if attr in attrvalues:
              attr_dict[attr] = deepcopy(attrvalues.get(attr))
          data[id_] = attr_dict
      else:
        # All or None policy is enforced, if one of the objects
        # is not available in cache, then we return empty
        # TODO(dan): cannot distinguish network failures vs
        # id not found in memcache, both scenarios return empty list
        return None
    return data

  def add(self, category, resource, data, expiration_time=0):
    """ add data to mem cache

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data: dictionary containing ids and attrs

    Returns:
      None on any errors
      Mapping of DTO formatted string, e.g. JSON string representation
    """
    if not self.is_caching_supported(category, resource):
      return None
    entries = {}
    cache_key = self.get_key(category, resource)
    if cache_key is None:
      return None
    # TODO(dan): use memcache.Client.add_multi() instead of add()
    for key in data.keys():
      cache_key = cache_key + ":" + str(key)
      cache_data = self.memcache_client.gets(cache_key)
      if cache_data is None:
        if self.memcache_client.add(cache_key,
                                    data.get(key),
                                    expiration_time) is False:
          # We stop processing any further
          # TODO(ggrcdev): Should we throw exceptions
          # and/or log critical events
          return None
        else:
          entries[key] = data
      else:
        # This could occur on import scenarios
        #
        if self.memcache_client.cas(cache_key,
                                    data.get(key),
                                    expiration_time) is False:
          # We stop processing any further
          # TODO(ggrcdev): Should we throw exceptions
          # and/or log critical events
          return None
        else:
          entries[key] = data
    return entries

  def update(self, category, resource, data, expiration_time):
    """ Update items from mem cache for specified data

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      filter: dictionary containing ids and attrs

    Returns:
      None on any errors
      Mapping of DTO formatted string, e.g. JSON string representation
    """
    if not self.is_caching_supported(category, resource):
      return None
    entries = {}
    cache_key = self.get_key(category, resource)
    if cache_key is None:
      return None
    # TODO(ggrcdev): use memcache.Client.cas_multi(),
    # get_multi() instead of cas(), gets()
    #
    for key in data.keys():
      id_ = cache_key + ":" + str(key)
      if self.memcache_client.cas(id_,
                                  data.get(key),
                                  expiration_time) is False:
        # RPC Error or value is not id is not found in cache.
        # Cannot proceed further with update (All or None) policy
        return None
      else:
        entries[key] = data
    return entries

  def remove(self, category, resource, data, lockadd_seconds=0):
    """ delete items from mem cache for specified data

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data: List of keys

    Returns:
      None on any errors
      mapping of DTO formatted string, e.g. JSON string representation
    """
    if not self.is_caching_supported(category, resource):
      return None
    entries = {}
    cache_key = self.get_key(category, resource)
    if cache_key is None:
      return None
    # TODO(dan): use memcache.Client.delete_multi(),
    # get_multi() instead of delete(), gets()
    #
    for key in data.keys():
      id_ = cache_key + ":" + str(key)
      retvalue = self.memcache_client.delete(id_, lockadd_seconds)
      # Log the event of delete failures
      if retvalue == 0:
        # retvalue of 0 indicates Network failure,
        # Cannot proceed further with delete (All or None) policy
        return None
      elif retvalue == 2:
        # retvalue of 2 indicates Success
        entries[key] = data
      elif retvalue == 1:
        # retvalue of 1 indicates id_ is not present in memcache
        # (could be expired), proceed with next entry
        continue
      else:
        # Any other return value,
        # Cannot proceed further with delete (All or None) policy
        #
        return None
    return entries

  def add_multi(self, data, expiration_time=0):
    """ Add multiple entries to memcache
    There are limits to size of data in memcache

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data: dictionary containing ids and dictionary of attrs

    Returns:
      memcache client API add_multi
    """
    # TODO(dan): import scenarios, add will return non-empty list,
    # we should invoke update_multi for those items
    #
    return self.memcache_client.add_multi(data, expiration_time)

  def get_multi(self, data):
    """ Get multiple entries from memcache
    There are limits to size of data in memcache

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data: dictionary containing ids

    Returns:
      memcache client API get_multi
    """
    return self.memcache_client.get_multi(data, '', None, True)

  def update_multi(self, data, expiration_time=0):
    """ update multiple entries to memcache
    There are limits to size of data in memcache

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data: dictionary containing ids and dictionary of attrs

    Returns:
      memcache client API cas_multi (compare and set)
    """
    return self.memcache_client.cas_multi(data, expiration_time)

  def remove_multi(self, data, lockadd_seconds):
    """ delete multiple entries to memcache

    Args:
      category: collection or stub
      resource: regulation, controls, etc.
      data:  list of keys

    Returns:
      memcache client API delete_multi
    """
    return self.memcache_client.delete_multi(data, lockadd_seconds)

  def clean(self):
    """ flush everything from memcache """
    return self.memcache_client.flush_all()


class _Decorated(object):
  """Decorated class."""

  def __init__(self, function):
    self.memcache_client = memcache.Client()
    self.function = function

  @property
  def active(self):
    return settings.MEMCACHE_MECHANISM

  @property
  def superhot_cache(self):
    """Property,

    link to flask.g global context with unique attr name generation."""
    if not hasattr(flask, self.get_key_prefix()):
      setattr(flask.g, self.get_key_prefix(), {})
    return getattr(flask.g, self.get_key_prefix())

  @superhot_cache.setter
  def superhot_cache(self, data):
    return setattr(flask.g, self.get_key_prefix(), data)

  def get_key_prefix(self):
    return "{}.{}".format(self.function.__module__, self.function.__name__)

  @staticmethod
  def get_key_suffix(*args, **kwargs):
    """Retun the suffix part of key."""
    key_args = list(args)
    for pair in kwargs.iteritems():
      key_args.extend(pair)
    return ','.join([str(a) for a in key_args])

  def get_key(self, *args, **kwargs):
    return "{}:{}".format(self.get_key_prefix(),
                          self.get_key_suffix(*args, **kwargs))

  def __call__(self, *args, **kwargs):
    if not self.active:
      return self.function(*args, **kwargs)
    if self.get_key_suffix(*args, **kwargs) in self.superhot_cache:
      return self.superhot_cache[self.get_key_suffix(*args, **kwargs)]
    key = self.get_key(*args, **kwargs)
    get_value = self.memcache_client.get(key)
    if get_value is not None:
      return get_value
    result = self.function(*args, **kwargs)
    self.memcache_client.add(key, result)
    self.superhot_cache[self.get_key_suffix(*args, **kwargs)] = result
    return result

  def invalidate_cache(self, *args, **kwargs):
    """Invalidate cached data."""
    if not self.active:
      return
    self.memcache_client.delete(self.get_key(*args, **kwargs))
    self.superhot_cache = {}


def cached(function):
  """Cached decorated functions that allowed to save data in memcache. """
  return _Decorated(function)
