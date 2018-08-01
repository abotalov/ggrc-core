/*
  Copyright (C) 2018 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import {getComponentVM} from '../../../../js_specs/spec_helpers';
import Component from '../object-state-toolbar';

describe('object-state-toolbar component', function () {
  let vm;

  beforeEach(function () {
    vm = getComponentVM(Component);
  });

  describe('hasPreviousState() method', function () {
    it('returns true if instance has previous state', function () {
      vm.attr('instance.previousStatus', 'In Progress');
      expect(vm.hasPreviousState()).toBe(true);
    });

    it('returns false if instance has not previous state', function () {
      vm.attr('instance.previousStatus', undefined);
      expect(vm.hasPreviousState()).toBe(false);
    });
  });
});
