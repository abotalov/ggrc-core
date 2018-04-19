import json
import random
import string
import time

import requests

BASE_URL = "http://localhost:8080"
USER = "user@example.com"

headers = {'X-Requested-By': 'GGRC',
           'Content-Type': 'application/json'}


session = requests.Session()
session.headers = headers


def set_session_cookie():
  session.get(BASE_URL + "/_ah/login?email={}&action=Login".format(USER))
  session.get(BASE_URL + "/login")


def create_control():
  url = BASE_URL + "/api/controls"
  title = "".join(random.choice(string.ascii_letters) for _ in range(15))
  request_body = [{
    "control": {
      'access_control_list': [
        {'person': {'type': 'Person', 'id': 1}, 'ac_role_id': 49}],
      'assertions': None,
      'categories': None,
      'context': None,
      'custom_attribute_definitions': [],
      'custom_attribute_values': [],
      'description': '',
      'fraud_related': None,
      'key_control': None,
      'kind': None,
      'means': None,
      'notes': '',
      'recipients': u'Admin,Primary Contacts,Secondary Contacts',
      'selected': False,
      'send_by_default': True,
      'slug': '',
      'status': u'Draft',
      'test_plan': '',
      'title': title,
      'url': '',
      'verify_frequency': None
    }}]
  request_body = json.dumps(request_body)
  response = session.post(url=url, data=request_body)
  assert response.status_code == 200
  return title


def query(title):
  url = BASE_URL + "/query"
  request_body = [{
    "filters": {
      "expression": {
        "left": "title",
        "op": {"name": "="},
        "right": title
      }
    },
    "object_name": "Control",
    "type": "values"
  }]
  request_body = json.dumps(request_body)
  response = session.post(url=url, data=request_body)
  count = json.loads(response.content)[0]["Control"]["count"]
  return count


set_session_cookie()


for i in range(20):
  print "Attempt {}".format(i)
  title1 = create_control()
  title2 = create_control()
  time.sleep(1)
  query(title1)
  if query(title2) == 0:
    print "Failed to search title: {}".format(title2)
