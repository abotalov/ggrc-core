/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from './collapsible-panel-body.mustache';

const tag = 'collapsible-panel-body';
/**
 * Collapsible Panel component to add collapsing behavior
 */
export default can.Component.extend({
  tag,
  template,
  viewModel: {
    renderContent: function () {
      return this.attr('softMode') || this.attr('expanded');
    },
    softMode: false,
    expanded: null,
  },
});
