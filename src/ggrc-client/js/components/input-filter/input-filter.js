/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from './templates/input-filter.mustache';

const tag = 'input-filter';

export default can.Component.extend({
  template,
  tag,
  viewModel: {
    value: '',
    excludeSymbols: '@',
    placeholder: '@',
    name: '@',
    label: '@',
    required: false,
    tooltipTitle: '@',
    tabindex: 0,
    autofocus: false,
  },
  events: {
    cleanUpInput(el) {
      const vm = this.viewModel;
      const regex = new RegExp(`[${vm.attr('excludeSymbols')}]`, 'gi');

      el.val(el.val().replace(regex, ''));
    },
    '.input-filter input': 'cleanUpInput',
  },
});
