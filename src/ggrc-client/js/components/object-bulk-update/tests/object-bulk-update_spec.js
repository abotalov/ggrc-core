/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import Component from '../object-bulk-update';
import * as stateUtils from '../../../plugins/utils/state-utils';
import tracker from '../../../tracker';
import Mappings from '../../../models/mappers/mappings';

describe('object-bulk-update component', function () {
  let events;

  beforeAll(function () {
    events = Component.prototype.events;
  });

  describe('viewModel() method', function () {
    let parentViewModel;
    let method;
    let targetStates;
    let mappingType;
    let result;

    beforeEach(function () {
      parentViewModel = new can.Map();
      method = Component.prototype.viewModel;
      mappingType = {
        type: 'the same type',
      };
      targetStates = ['Assigned', 'In Progress'];

      spyOn(stateUtils, 'getBulkStatesForModel')
        .and.returnValue(targetStates);
      spyOn(Mappings, 'getMappingType')
        .and.returnValue(mappingType);

      result = method({type: 'some type'}, parentViewModel)();
    });

    it('returns correct type', function () {
      expect(result.type).toEqual('some type');
    });

    it('returns correct target states', function () {
      let actual = can.makeArray(result.targetStates);
      expect(actual).toEqual(targetStates);
    });

    it('returns correct target state', function () {
      expect(result.targetState).toEqual('Assigned');
    });

    it('returns set reduceToOwnedItems flag', function () {
      expect(result.reduceToOwnedItems).toBeTruthy();
    });

    it('returns set showTargetState flag', function () {
      expect(result.showTargetState).toBeTruthy();
    });

    it('returns correct defaultSort', function () {
      expect(result.defaultSort.serialize()[0].key).toEqual('task due date');
    });

    it('returns correct availableTypes', function () {
      expect(result.availableTypes())
        .toEqual(mappingType);
    });
  });

  describe('closeModal event', function () {
    let event;
    let element;

    beforeAll(function () {
      let scope;
      element = {
        trigger: jasmine.createSpy(),
      };
      element.find = jasmine.createSpy().and.returnValue(element);
      scope = {
        element: element,
      };

      event = events.closeModal.bind(scope);
    });

    it('closes modal if element defined', function () {
      event();

      expect(element.trigger).toHaveBeenCalledWith('click');
    });
  });

  describe('.btn-cancel click event', function () {
    it('closes modal', function () {
      let context = {
        closeModal: jasmine.createSpy(),
      };
      let event = events['.btn-cancel click'].bind(context);

      event();

      expect(context.closeModal).toHaveBeenCalled();
    });
  });

  describe('.btn-update click event', function () {
    let event;
    let context;

    beforeEach(function () {
      context = {
        viewModel: new can.Map(),
      };
      event = events['.btn-update click'].bind(context);

      spyOn(tracker, 'start').and.returnValue(() => {});
    });

    it('invokes update callback', function () {
      context.viewModel.callback = jasmine.createSpy()
        .and.returnValue({
          then() {},
        });
      context.viewModel.attr('selected', [1]);
      context.viewModel.attr('targetState', 'In Progress');

      event();

      expect(context.viewModel.callback)
        .toHaveBeenCalled();
    });
  });

  describe('"inserted" event handler', function () {
    let event;
    let context;

    beforeEach(function () {
      context = {
        viewModel: new can.Map({
          submitCbs: {
            fire: jasmine.createSpy(),
          },
        }),
      };
      event = events.inserted.bind(context);
    });

    it('calls fire() of submitCbs attribute', function () {
      event();

      expect(context.viewModel.submitCbs.fire).toHaveBeenCalled();
    });
  });
});
