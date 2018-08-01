/*
  Copyright (C) 2018 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import {getComponentVM} from '../../../js_specs/spec_helpers';
import Component from '../dropdown/multiselect-dropdown';

describe('multiselect-dropdown component', function () {
  'use strict';

  describe('updateSelected() method', function () {
    let options;
    let viewModel;

    beforeEach(function () {
      viewModel = getComponentVM(Component);

      options = [
        {
          value: 'Draft',
        },
        {
          value: 'Active',
        },
        {
          value: 'Open',
        },
        {
          value: 'Deprecated',
        },
      ];

      viewModel.attr('options', options);
    });

    it('updateSelected() should add new item in "selected"',
      function () {
        let selected;
        let item = viewModel.attr('options')[1];
        item.checked = true;

        viewModel.updateSelected(item);
        selected = viewModel.attr('selected');

        expect(selected.length).toEqual(1);
        expect(selected[0].value).toEqual(item.value);
      }
    );

    it('updateSelected() should remove item from "selected"',
      function () {
        let selected = viewModel.attr('selected');
        let options = viewModel.attr('options');
        let item;

        expect(selected.length).toEqual(0);

        options.forEach(function (option) {
          option.checked = true;
          viewModel.updateSelected(option);
        });

        // we added all options in selected
        expect(selected.length).toEqual(options.length);

        item = viewModel.attr('options')[1];
        item.checked = false;

        // pass uchecked item
        viewModel.updateSelected(item);

        expect(selected.length).toEqual(options.length - 1);
      }
    );

    it('updateSelected() should not add duplicates in "selected"',
      function () {
        let selected;
        let item = viewModel.attr('options')[1];
        item.checked = true;

        // double call
        viewModel.updateSelected(item);
        viewModel.updateSelected(item);

        selected = viewModel.attr('selected');

        expect(selected.length).toEqual(1);
        expect(selected[0].value).toEqual(item.value);
      }
    );
  });

  describe('_displayValue attribute', function () {
    let viewModel;
    let options;
    let draftItem;
    let activeItem;
    let openItem;

    beforeEach(function () {
      viewModel = getComponentVM(Component);

      options = [
        {
          value: 'Draft',
        },
        {
          value: 'Active',
        },
        {
          value: 'Open',
        },
        {
          value: 'Deprecated',
        },
      ];

      viewModel.attr('options', options);

      draftItem = options[0];
      activeItem = options[1];
      openItem = options[2];
    });

    it('check "_displayValue" after add new "seleted"',
      function () {
        draftItem.checked = true;
        activeItem.checked = true;

        // select items
        viewModel.updateSelected(draftItem);
        viewModel.updateSelected(activeItem);

        expect(viewModel.attr('_displayValue'))
          .toEqual(draftItem.value + ', ' + activeItem.value);
      }
    );

    it('check "_displayValue" after remove item from "seleted"',
      function () {
        draftItem.checked = true;
        activeItem.checked = true;
        openItem.checked = true;

        // select items
        viewModel.updateSelected(draftItem);
        viewModel.updateSelected(activeItem);
        viewModel.updateSelected(openItem);

        // remove activeItem from 'selected' array
        activeItem.checked = false;
        viewModel.updateSelected(activeItem);

        // '_displayValue' should contain values of 'draftItem' and 'openItem' items
        expect(viewModel.attr('_displayValue'))
          .toEqual(draftItem.value + ', ' + openItem.value);
      }
    );
  });

  describe('"open/close" state of component', function () {
    let viewModel;

    beforeEach(function () {
      viewModel = getComponentVM(Component);
      viewModel.attr('options', [{value: 'someOption'}]);
    });

    it('open dropdown',
      function () {
        // click on dropdown input
        viewModel.openDropdown();

        // "window.click" event is triggered after click on dropdown input
        viewModel.changeOpenCloseState();
        expect(viewModel.attr('isOpen')).toEqual(true);
        expect(viewModel.attr('canBeOpen')).toEqual(false);
      }
    );

    it('close dropdown without changing of options',
      function () {
        spyOn(can, 'trigger');
        viewModel.attr('isOpen', true);
        viewModel.attr('_stateWasUpdated', false);

        // simulate "window.click" event
        viewModel.changeOpenCloseState();

        expect(viewModel.attr('isOpen')).toEqual(false);
        expect(viewModel.attr('canBeOpen')).toEqual(false);
        expect(can.trigger.calls.count()).toEqual(0);
      }
    );

    it('close dropdown with changing of options',
      function () {
        let item = viewModel.attr('options')[0];
        spyOn(can, 'trigger');
        viewModel.attr('isOpen', true);
        viewModel.attr('_stateWasUpdated', false);

        // change state of item
        item.checked = true;
        viewModel.updateSelected(item);

        // simulate "window.click" event
        viewModel.changeOpenCloseState();

        expect(viewModel.attr('isOpen')).toEqual(false);
        expect(viewModel.attr('canBeOpen')).toEqual(false);
        expect(can.trigger.calls.count()).toEqual(1);
      }
    );
  });
});
