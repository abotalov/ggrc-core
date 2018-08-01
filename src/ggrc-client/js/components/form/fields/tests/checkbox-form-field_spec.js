/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import {getComponentVM} from '../../../../../js_specs/spec_helpers';
import Component from '../checkbox-form-field';

describe('checkbox-form-field component', function () {
  'use strict';
  let viewModel;

  beforeEach(function () {
    viewModel = getComponentVM(Component);
    spyOn(viewModel, 'dispatch');
    viewModel.attr('fieldId', 'id');
  });

  it('does not fire valueChanged event on first value assignation', function () {
    viewModel.attr('value', true);
    expect(viewModel.dispatch).not.toHaveBeenCalled();
  });

  it('sets the value of the input', function () {
    viewModel.attr('value', true);
    expect(viewModel.attr('inputValue')).toEqual(true);
  });

  it('fires valueChanged event on input value change', function () {
    viewModel.attr('value', false);
    viewModel.attr('inputValue', true);
    expect(viewModel.dispatch).toHaveBeenCalledWith({
      type: 'valueChanged',
      fieldId: 'id',
      value: true,
    });
    viewModel.attr('inputValue', false);
    expect(viewModel.dispatch).toHaveBeenCalledWith({
      type: 'valueChanged',
      fieldId: 'id',
      value: false,
    });
  });
});
