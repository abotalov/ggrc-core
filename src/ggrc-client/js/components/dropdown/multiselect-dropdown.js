/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import template from './multiselect_dropdown.mustache';

export default can.Component.extend({
  tag: 'multiselect-dropdown',
  template,
  viewModel: {
    disabled: false,
    _stateWasUpdated: '',
    selected: [],
    plural: '@',
    placeholder: '@',
    element: '',
    define: {
      _displayValue: {
        get: function () {
          return this.attr('selected').map(function (item) {
            return item.attr('value');
          }).join(', ');
        },
      },
      _inputSize: {
        type: Number,
        get: function () {
          return this.attr('_displayValue').length;
        },
      },
      _selectedAll: {
        type: 'boolean',
        value: false,
        get: function () {
          let options = this.attr('options') || [];

          return Array.prototype.every.call(options, function (item) {
            return item.attr('checked');
          });
        },
        set: function (value) {
          let options = this.attr('options') || [];

          options.forEach(function (option) {
            option.attr('checked', value);
          });

          return value;
        },
      },
      isOpen: {
        type: 'boolean',
        value: false,
      },
      options: {
        type: '*',
        set: function (value) {
          let self = this;
          this.attr('selected', []);
          if (value) {
            value.forEach(function (item) {
              self.updateSelected(item);
            });

            return value;
          }

          return [];
        },
      },
    },
    updateSelected: function (item) {
      let selected = this.attr('selected');
      let index = -1;
      let duplicates;

      this.attr('_stateWasUpdated', true);

      if (item.checked) {
        duplicates = selected.filter(function (selectedItem) {
          return selectedItem.attr('value') === item.value;
        });

        if (duplicates.length > 0) {
          return;
        }

        selected.push(item);
        return;
      }

      index = selected.map(function (selectedItem) {
        return selectedItem.value;
      }).indexOf(item.value);

      if (index > -1) {
        selected.splice(index, 1);
      }
    },
    dropdownClosed: function (el, ev, scope) {
      // don't trigger event if state didn't change
      if (!this.attr('_stateWasUpdated')) {
        return;
      }

      let selected = this.attr('selected');

      this.attr('_stateWasUpdated', false);
      can.trigger(el, 'multiselect:closed', [selected]);
      this.dispatch({
        type: 'dropdownClose',
        selected: selected,
      });
    },
    changeOpenCloseState: function () {
      if (!this.attr('isOpen')) {
        if (this.attr('canBeOpen')) {
          this.attr('canBeOpen', false);
          this.attr('isOpen', true);
        }
      } else {
        this.attr('isOpen', false);
        this.attr('canBeOpen', false);
        this.dropdownClosed(this.element);
      }
    },
    openDropdown: function (el) {
      if (this.attr('disabled')) {
        return;
      }
      // we should save element of component.
      // it necessary for 'can.trigger'
      if (el && !this.element) {
        this.element = el;
      }

      // this attr needed when page has any components
      this.attr('canBeOpen', true);
    },
    dropdownBodyClick: function (ev) {
      ev.stopPropagation();
    },
  },
  events:
  {
    '{options} change': function (scope, ev, propertyName) {
      let target = ev.target;

      // igore all propetries except 'checked'
      if (propertyName.indexOf('checked') === -1) {
        return;
      }

      this.viewModel.updateSelected(target);

      can.trigger(this.element, 'multiselect:changed',
        [this.viewModel.attr('selected')]);
    },
    '{window} click': function () {
      if (this.viewModel.attr('disabled')) {
        return;
      }
      this.viewModel.changeOpenCloseState();
    },
  },
});
