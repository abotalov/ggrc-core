/*
  Copyright (C) 2018 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import updateService from '../../../plugins/utils/bulk-update-service';
import {getComponentVM} from '../../../../js_specs/spec_helpers';
import Component from '../bulk-update-button';
import * as NotifiersUtils from '../../../plugins/utils/notifiers-utils';

describe('bulk-update-button component', function () {
  let viewModel;
  let events;

  beforeAll(function () {
    viewModel = getComponentVM(Component);
    events = Component.prototype.events;
  });

  describe('button click event', function () {
    let event;
    beforeAll(function () {
      event = events['a click'].bind({viewModel});
      spyOn(viewModel, 'openBulkUpdateModal');
    });

    it('should open ObjectBulkUpdate modal', function () {
      let type = 'some model';
      let element = {};
      viewModel.attr('model', {
        model_singular: type,
      });

      event(element);

      expect(viewModel.openBulkUpdateModal)
        .toHaveBeenCalledWith(jasmine.any(Object), type);
    });
  });

  describe('updateObjects method', function () {
    let updateDfd;
    let context;
    let args;
    let resMessage;
    let el;
    const parentEl = {};

    beforeEach(function () {
      el = {
        closest: jasmine.createSpy().and.returnValue(parentEl),
      };
      context = {
        closeModal: jasmine.createSpy(),
      };
      args = {
        selected: [1],
        options: {},
      };

      viewModel.attr('model', {
        name_singular: 'Some Model',
      });
      resMessage = 'items updated';
      updateDfd = can.Deferred();

      spyOn(can, 'trigger');
      spyOn(NotifiersUtils, 'notifier');
      spyOn(updateService, 'update')
        .and.returnValue(updateDfd);

      spyOn(viewModel, 'getResultNotification')
        .and.returnValue(resMessage);

      viewModel.updateObjects(el, context, args);
    });

    it('closes ObjectBulkUpdate modal', function () {
      expect(context.closeModal).toHaveBeenCalled();
    });

    it('shows notification about bulk progress', function () {
      expect(NotifiersUtils.notifier)
        .toHaveBeenCalledWith('progress',
          'Some Model update is in progress. This may take several minutes.');
    });

    it('shows notification about bulk update result', function () {
      updateDfd.resolve([{status: 'updated'}]);

      expect(viewModel.getResultNotification)
        .toHaveBeenCalledWith(viewModel.attr('model'), 1);
      expect(NotifiersUtils.notifier)
        .toHaveBeenCalledWith('info', resMessage);
    });

    it('triggers TreeView refresh when some items updated', function () {
      updateDfd.resolve([{status: 'updated'}]);

      expect(el.closest).toHaveBeenCalled();
      expect(can.trigger)
        .toHaveBeenCalledWith(parentEl, 'refreshTree');
    });

    it('does not trigger TreeView refresh when no item was updated',
      function () {
        updateDfd.resolve([]);

        expect(el.closest).not.toHaveBeenCalled();
        expect(can.trigger)
          .not.toHaveBeenCalled();
      });

    it('does not show notification when update failed', function () {
      updateDfd.reject();

      expect(viewModel.getResultNotification)
        .not.toHaveBeenCalled();
      expect(NotifiersUtils.notifier)
        .not.toHaveBeenCalledWith('info', jasmine.any(String));
    });
  });

  describe('getResultNotification method', function () {
    let model = {
      name_singular: 'Task',
      name_plural: 'Tasks',
    };

    it('returns correct message when no objects were updated', function () {
      let expected = 'No tasks were updated.';
      let actual = viewModel.getResultNotification(model, 0);

      expect(actual).toEqual(expected);
    });

    it('returns correct message when 1 object was updated', function () {
      let expected = '1 task was updated successfully.';
      let actual = viewModel.getResultNotification(model, 1);

      expect(actual).toEqual(expected);
    });

    it('returns correct message when multiple objects were updated',
      function () {
        let expected = '4 tasks were updated successfully.';
        let actual = viewModel.getResultNotification(model, 4);

        expect(actual).toEqual(expected);
      });
  });
});
