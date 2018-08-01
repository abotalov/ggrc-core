/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from './templates/tree-no-results.mustache';

export default can.Component.extend({
  tag: 'tree-no-results',
  template,
  viewModel: {
    define: {
      text: {
        value: 'No results, please check your filter criteria',
        set: function (value) {
          return value || 'No results...';
        },
      },
      show: {
        set: function (value) {
          return value || false;
        },
      },
    },
  },
});
