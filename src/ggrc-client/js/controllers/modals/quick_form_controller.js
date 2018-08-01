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
    if (this.element.data('force-refresh')) {
      this.options.instance.refresh();
    }
  },
  'input, textarea, select change': function (el) {
    let self = this;
    let val;
    let prop;
    let oldValue;
    if (el.data('toggle') === 'datepicker') {
      val = el.datepicker('getDate');
      prop = el.attr('name');
      oldValue = this.options.instance.attr(prop);

      if (moment(val).isSame(oldValue)) {
        return;
      }
      can.when(this.options.instance.refresh()).then(function () {
        self.options.instance.attr(prop, val);
        self.options.instance.save();
      });
      return;
    }
    if (!el.is('[data-lookup]')) {
      this.set_value_from_element(el);
      setTimeout(function () {
        this.options.instance.save();
      }.bind(this), 100);
    }
  },
  autocomplete_select: function (el, event, ui) {
    let self = this;
    let prop = el.attr('name').split('.').slice(0, -1).join('.');
    if (this._super(...arguments) !== false) {
      setTimeout(function () {
        self.options.instance.save().then(function () {
          let obj = self.options.instance.attr(prop);
          if (obj.attr) {
            obj.attr('saved', true);
          }
        });
      }, 100);
    } else {
      return false;
    }
  },
  'input, select, textarea click': function (el, ev) {
    if (el.data('toggle') === 'datepicker') {
      return;
    }
    if (this._super) {
      this._super(...arguments);
    }
    ev.stopPropagation();
  },
  '.dropdown-menu > li click': function (el, ev) {
    let self = this;
    ev.stopPropagation();
    this.set_value({name: el.data('name'), value: el.data('value')});
    setTimeout(function () {
      self.options.instance.save();
      $(el).closest('.open').removeClass('open');
    }, 100);
  },
  'button[data-name][data-value]:not(.disabled), a.undoable[data-toggle*=modal] click': function (el, ev) {
    let self = this;
    let name = el.data('name');
    let oldValue = {};
    let action;
    let openclose;
    let isOpened;
    const instance = self.options.instance;

    if (el.data('openclose')) {
      action = el.data('openclose');
      openclose = el.closest('.item-main').find('.openclose');
      isOpened = openclose.hasClass('active');

      // We can't use main.openclose(action) here because content may not be loaded yet
      if (action === 'trigger') {
        openclose.trigger('click');
      } else if (action === 'close' && isOpened) {
        openclose.trigger('click');
      } else if (action === 'open' && !isOpened) {
        openclose.trigger('click');
      }
    }

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
  'a.undo click': function (el, ev) {
    let self = this;
    let newValue = this.options.instance.attr('_undo').shift();
    ev.stopPropagation();

    this.options.instance.attr('_disabled', 'disabled');
    this.options.instance
      .refresh()
      .then(function (instance) {
        can.each(newValue, function (value, name) {
          self.set_value({name: name, value: value});
        });
        return instance.save();
      }).then(function () {
        self.options.instance.attr('_disabled', '');
      });
  },
});
