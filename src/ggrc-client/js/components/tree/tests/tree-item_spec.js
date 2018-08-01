/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import {getComponentVM} from '../../../../js_specs/spec_helpers';
import Component from '../tree-item';

describe('tree-item component', function () {
  'use strict';

  let vm;

  beforeEach(function () {
    vm = getComponentVM(Component);
  });

  describe('selectableSize property', function () {
    it('selectedColumns.length < 4', function () {
      vm.attr('selectedColumns', ['a', 'b', 'c']);

      expect(vm.attr('selectableSize')).toEqual(1);
    });

    it('selectedColumns.length = 5', function () {
      vm.attr('selectedColumns', ['a', 'b', 'c', 'd', 'e']);

      expect(vm.attr('selectableSize')).toEqual(2);
    });

    it('selectedColumns.length > 7', function () {
      vm.attr('selectedColumns', ['a', 'b', 'c', 'd', 'e', 'f', 'g']);

      expect(vm.attr('selectableSize')).toEqual(3);
    });
  });
});
