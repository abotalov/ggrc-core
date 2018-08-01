/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import {getComponentVM} from '../../../../../js_specs/spec_helpers';
import Component from '../person-form-field';

describe('person-form-field component', function () {
  'use strict';
  let viewModel;

  beforeEach(function () {
    viewModel = getComponentVM(Component);
    spyOn(viewModel, 'dispatch');
    viewModel.attr('fieldId', 1);
  });

  it('does not fire valueChanged event' +
    ' on first value assignation', function () {
    viewModel.attr('value', undefined);
    expect(viewModel.dispatch).not.toHaveBeenCalled();
  });

  it('sets the value of the input', function () {
    viewModel.attr('value', 'test');
    expect(viewModel.attr('inputValue')).toEqual('test');
  });

  it('does not fire valueChanged event if value wasn\'t changed', function () {
    viewModel.attr('value', {});
    viewModel.attr('inputValue', 1);
    viewModel.dispatch.calls.reset();
    viewModel.attr('inputValue', 1);
    expect(viewModel.dispatch).not.toHaveBeenCalled();
  });

  it('fires valueChanged event on input value change', function () {
    viewModel.attr('value', '');
    viewModel.attr('inputValue', 1);
    expect(viewModel.dispatch).toHaveBeenCalledWith({
      type: 'valueChanged',
      fieldId: 1,
      value: viewModel.attr('inputValue'),
    });
    viewModel.attr('inputValue', 2);
    expect(viewModel.dispatch).toHaveBeenCalledWith({
      type: 'valueChanged',
      fieldId: 1,
      value: viewModel.attr('inputValue'),
    });
  });

  it('unsets a person and fires valueChanged event', function () {
    viewModel.attr('value', '');
    viewModel.attr('inputValue', 'newValue');
    viewModel.dispatch.calls.reset();
    viewModel.unsetPerson(null, null, new Event('mock'));
    expect(viewModel.dispatch).toHaveBeenCalledWith({
      type: 'valueChanged',
      fieldId: 1,
      value: null,
    });
  });
});
