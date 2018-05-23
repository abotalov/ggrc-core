/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import Component from '../input-filter';

describe('GGRC.Components.inputFilter', () => {
  let viewModel;
  let events;

  beforeAll(() => {
    events = Component.prototype.events;
  });

  beforeEach(() => {
    viewModel = new (can.Map.extend(Component.prototype.viewModel));
  });

  describe('cleanUpInput() method', () => {
    let handler;
    let fakeElem;

    beforeEach(() => {
      fakeElem = $('<input value="test"/>');
      handler = events.cleanUpInput.bind({viewModel: viewModel});
    });

    it('should exclude single symbol entry', () => {
      viewModel.attr('excludeSymbols', 'e');
      handler(fakeElem);

      expect(fakeElem.val()).toBe('tst');
    });

    it('should exclude multiple entries', () => {
      viewModel.attr('excludeSymbols', 't');
      handler(fakeElem);

      expect(fakeElem.val()).toBe('es');
    });

    it('should not do anything with empty string', () => {
      viewModel.attr('excludeSymbols', '');
      handler(fakeElem);

      expect(fakeElem.val()).toBe('test');
    });
  });
});
