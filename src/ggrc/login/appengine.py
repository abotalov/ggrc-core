# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Login handler for using App Engine authentication with Flask-Login

Assumes app.yaml is configured with:

..
  handlers:
    - url: /login
      script: <wsgi_app path>
      login: required

E.g., ``login: required`` must be specified *at least* for the '/login' route.
"""

from google.appengine.api import users
import flask
import flask_login

from ggrc.login import common


def get_user():
  """Get current user using appengine authentication."""
  ae_user = users.get_current_user()
  email = ae_user.email()
  nickname = ae_user.nickname()
  user = common.find_or_create_user_by_email(email, name=nickname)
  return user


def login():
  """Log in current user."""
  user = get_user()
  if user.system_wide_role != 'No Access':
    flask_login.login_user(user)
    return flask.redirect(common.get_next_url(
        flask.request, default_url=flask.url_for('dashboard')))

  flask.flash(u'You do not have access. Please contact your administrator.',
              'alert alert-info')
  return flask.redirect('/')


def logout():
  flask_login.logout_user()
  return flask.redirect(users.create_logout_url(common.get_next_url(
      flask.request, default_url=flask.url_for('index'))))
