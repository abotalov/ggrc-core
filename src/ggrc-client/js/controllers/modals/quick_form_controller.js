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
  'button[data-name][data-value]:not(.disabled), a.undoable[data-toggle*=modal] click': function (el, ev) {
    let self = this;
    let name = el.data('name');
    let oldValue = {};
    const instance = self.options.instance;

    oldValue[name] = instance.attr(name);
    if (el.data('also-undo')) {
      can.each(el.data('also-undo').split(','), function (attrname) {
        attrname = attrname.trim();
        oldValue[attrname] = instance.attr(attrname);
      });
    }

    // Check if the undo button was clicked:
    instance.attr('_undo') || instance.attr('_undo', []);

    if (el.is('[data-toggle*=modal')) {
      setTimeout(function () {
        $('.modal:visible').one('modal:success', function () {
          instance.attr('_undo').unshift(oldValue);
        });
      }, 100);
    } else {
      ev.stopPropagation();
      instance.attr('_undo').unshift(oldValue);

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
    }
  },
});
