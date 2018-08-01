/*
  Copyright (C) 2018 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import Component from '../tree-item-actions';
import {getComponentVM} from '../../../../js_specs/spec_helpers';
import Permission from '../../../permission';

describe('tree-item-actions component', function () {
  let viewModel;

  beforeEach(() => {
    viewModel = getComponentVM(Component);
    viewModel.attr('instance', new can.Map());
  });

  describe('isAllowedToMap get() method', () => {
    beforeEach(() => {
      viewModel.attr('isSnapshot', false);
    });
    describe('returns false', () => {
      describe('if instance type is Assessment', ()=> {
        beforeEach(()=> {
          viewModel.attr('instance', {
            type: 'Assessment',
          });
        });

        it('and there is no audit', () => {
          viewModel.attr('instance.audit', null);

          let result = viewModel.attr('isAllowedToMap');

          expect(result).toBe(false);
        });

        it('and there is audit but it is not allowed to read audit', () => {
          viewModel.attr('instance.audit', {});
          spyOn(Permission, 'is_allowed_for').and.returnValue(false);

          let result = viewModel.attr('isAllowedToMap');

          expect(result).toBe(false);
        });
      });

      it('if instance type is in forbiddenMapList', () => {
        viewModel.attr('instance.type', 'Workflow');

        let result = viewModel.attr('isAllowedToMap');

        expect(result).toBe(false);
      });
    });

    describe('returns true', () => {
      describe('if instance type is Assessment', ()=> {
        beforeEach(()=> {
          viewModel.attr('instance', {
            type: 'Assessment',
          });
        });

        it('there is audit and it is allowed to read audit', () => {
          viewModel.attr('instance.audit', {});
          spyOn(Permission, 'is_allowed_for').and.returnValue(true);

          let result = viewModel.attr('isAllowedToMap');

          expect(result).toBe(true);
        });
      });

      it('if instance type is not in forbiddenMapList', () => {
        viewModel.attr('instance.type', 'Type');

        let result = viewModel.attr('isAllowedToMap');

        expect(result).toBe(true);
      });
    });
  });
});
