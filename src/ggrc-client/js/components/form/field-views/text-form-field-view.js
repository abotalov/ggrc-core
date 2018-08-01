/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from './text-form-field-view.mustache';

export default can.Component.extend({
  tag: 'text-form-field-view',
  template,
  viewModel: {
    value: null,
    disabled: false,
  },
});
