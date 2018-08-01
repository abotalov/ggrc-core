/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

(function (GGRC, moment) {
  GGRC.mustache_path = '/static/mustache';

  GGRC.extensions = GGRC.extensions || [];
  if (!GGRC.widget_descriptors) {
    GGRC.widget_descriptors = {};
  }
})(window.GGRC = window.GGRC || {}, moment);
