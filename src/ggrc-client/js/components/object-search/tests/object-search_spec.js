/*
  Copyright (C) 2018 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import Component from '../object-search';
import Mappings from '../../../models/mappers/mappings';

describe('object-search component', function () {
  'use strict';

  let viewModel;
  let parentViewModel;

  beforeEach(function () {
    parentViewModel = new can.Map();
    viewModel = new Component.prototype.viewModel({}, parentViewModel)();
  });

  describe('availableTypes() method', function () {
    it('correctly calls getMappingTypes', function () {
      let result;
      spyOn(Mappings, 'getMappingTypes').and.returnValue('types');
      viewModel.attr('object', 'testObject');

      result = viewModel.availableTypes();
      expect(Mappings.getMappingTypes).toHaveBeenCalledWith('testObject',
        ['TaskGroupTask', 'TaskGroup', 'CycleTaskGroupObjectTask'], []);
      expect(result).toEqual('types');
    });
  });

  describe('onSubmit() method', function () {
    it('sets resultsRequested flag to true', function () {
      viewModel.attr('resultsRequested', false);

      viewModel.onSubmit();

      expect(viewModel.attr('resultsRequested')).toBe(true);
    });
  });
});
