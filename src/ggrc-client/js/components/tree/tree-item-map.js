/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from './templates/tree-item-map.mustache';

let viewModel = can.Map.extend({
  define: {
    title: {
      type: String,
      value: 'Map to this Object',
    },
    model: {
      type: '*',
      get: function () {
        return this.attr('instance.model');
      },
    },
    objectParams: {
      type: String,
      get: function () {
        let instance = this.attr('instance');
        let params = {
          section: {
            id: instance.id,
            title: instance.title,
            description: instance.description,
          },
        };

        return JSON.stringify(params);
      },
    },
  },
  instance: null,
  cssClasses: null,
  disableLink: false,
});

export default can.Component.extend({
  tag: 'tree-item-map',
  template,
  viewModel,
  events: {
    'a click': function (el, ev) {
      let viewModel = this.viewModel;
      let instance = viewModel.attr('instance');

      if (!viewModel.attr('disableLink')) {
        if (instance.attr('type') === 'Assessment') {
          el.data('type', instance.attr('assessment_type'));
        }
        import(/* webpackChunkName: "mapper" */ '../../controllers/mapper/mapper')
          .then(() => {
            can.trigger(el, 'openMapper', ev);
          });
      }

      viewModel.attr('disableLink', true);

      // prevent open of two mappers
      setTimeout(function () {
        viewModel.attr('disableLink', false);
      }, 300);

      ev.preventDefault();
      return false;
    },
  },
});
