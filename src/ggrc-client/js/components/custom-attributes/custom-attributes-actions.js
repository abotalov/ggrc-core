/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from './custom-attributes-actions.mustache';

export default can.Component.extend({
  tag: 'custom-attributes-actions',
  template,
  viewModel: {
    formEditMode: false,
    edit: function () {
      this.attr('formEditMode', true);
    },
  },
});
