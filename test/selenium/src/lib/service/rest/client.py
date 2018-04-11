# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""REST API client."""
# pylint: disable=redefined-builtin

import json
import urlparse

import requests

from lib import environment, url
from lib.service.rest.template_provider import TemplateProvider


class RestClient(object):
  """Client for HTTP interactions with GGRC's REST API."""
  BASIC_HEADERS = {'X-Requested-By': 'GGRC',
                   'Content-Type': 'application/json',
                   'Accept-Encoding': 'gzip, deflate, br'}

  STATUS_CODES = {'OK': 200,
                  'FAIL': [400, 404, 500]}

  def __init__(self, endpoint):
    self.is_api = "" if endpoint == url.QUERY else url.API
    self.endpoint_url = urlparse.urljoin(
        environment.app_url, "/".join([self.is_api, endpoint]))
    self.session = requests.Session()
    self.session.headers = self.BASIC_HEADERS
    self.login()

  def login(self):
    """Set dev_appserver_login and session cookies."""
    self.session.get(url.Urls().gae_login)
    self.session.get(url.Urls().login)

  def create_object(self, type, **kwargs):
    """Create object or make other operations used POST request and
    return raw response.
    """
    create_obj_req_body = self.generate_body(type_name=type, **kwargs)
    create_obj_resp = self.session.post(
        url=self.endpoint_url, data=create_obj_req_body)
    return create_obj_resp

  def update_object(self, href, **kwargs):
    """Update object used GET, POST requests and return raw response."""
    href_url = urlparse.urljoin(environment.app_url, href)
    obj_resp = self.get_object(href_url)
    obj_resp_headers = obj_resp.headers
    obj_resp_body = obj_resp.text
    update_obj_req_headers = self.req_headers_from_resp_headers(
        resp_headers=obj_resp_headers)
    update_obj_req_body = self.update_body(body=obj_resp_body, **kwargs)
    update_obj_resp = self.session.put(
        url=href_url, data=update_obj_req_body, headers=update_obj_req_headers)
    return update_obj_resp

  def delete_object(self, href):
    """Delete object used GET, POST requests and return raw response."""
    href_url = urlparse.urljoin(environment.app_url, href)
    obj_resp_headers = self.get_object(href_url).headers
    del_obj_req_headers = self.req_headers_from_resp_headers(
        resp_headers=obj_resp_headers)
    del_obj_resp = self.session.delete(
        url=href_url, headers=del_obj_req_headers)
    return del_obj_resp

  def get_object(self, href):
    """Get object used GET request and return raw response."""
    href_url = urlparse.urljoin(environment.app_url, href)
    get_obj_resp = self.session.get(url=href_url)
    return get_obj_resp

  def generate_body(self, type_name, **kwargs):
    """Generate body of HTTP request based on JSON representation."""
    body = TemplateProvider.generate_template_as_dict(
        json_tmpl_name=type_name, **kwargs)
    if not self.is_api:
      body = body[type_name]
    return json.dumps([body]).encode("string-escape")

  @staticmethod
  def req_headers_from_resp_headers(resp_headers=None):
    """Return request headers from response headers."""
    headers = {}
    if resp_headers:
      headers["If-Match"] = resp_headers["Etag"]
      headers["If-Unmodified-Since"] = resp_headers["Last-Modified"]
    return headers

  @staticmethod
  def update_body(body, **kwargs):
    """Update body of HTTP request based on JSON representation."""
    return json.dumps(TemplateProvider.update_template_as_dict(
        json_data_str=body, **kwargs)).encode("string-escape")
