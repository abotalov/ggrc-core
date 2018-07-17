/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import ModalsController from './modals_controller';
import {isNull, isUndefined} from 'lodash';

export default ModalsController({
  pluginName: 'ggrc_controllers_quick_form',
  defaults: {
    model: null,
    instance: null,
  },
}, {
  init: function () {
    if (this.options.instance && !this.options.model) {
      this.options.model = this.options.instance.constructor;
    }
    this.options.$content = this.element;
  },
  'button[data-name][data-value]:not(.disabled)': function (el, ev) {
    let self = this;
    const instance = self.options.instance;

    ev.stopPropagation();

    instance.attr('_disabled', 'disabled');
    instance
      .refresh()
      .then(function (instance) {
        self.set_value({name: el.data('name'), value: el.data('value')});
        return instance.save();
      })
      .then(function () {
        const modelType = el.data('objectType');
        const id = el.data('objectId');
        if (modelType && !isNull(id) && !isUndefined(id)) {
          return CMS.Models[modelType].findOne({id});
        }
      })
      .then(function () {
        instance.attr('_disabled', '');
      });
  },
});
