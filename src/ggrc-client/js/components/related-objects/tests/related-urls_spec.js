/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import Component from '../related-urls';
import {getComponentVM} from '../../../../js_specs/spec_helpers';
import Permission from '../../../permission';
import * as NotifiersUtils from '../../../plugins/utils/notifiers-utils';

describe('GGRC.Components.relatedUrls', function () {
  'use strict';

  let viewModel;
  let instance;

  beforeEach(function () {
    viewModel = getComponentVM(Component);
    instance = {};
    viewModel.attr('instance', instance);
  });

  describe('canAddUrl get() method', ()=> {
    beforeEach(()=> {
      spyOn(Permission, 'is_allowed_for');
    });

    it('returns false if user can not update instance', ()=> {
      Permission.is_allowed_for.and.returnValue(false);

      let result = viewModel.attr('canAddUrl');

      expect(result).toBe(false);
    });

    it(`returns false if user can update instance 
        but edit is disabled in the component`, ()=> {
        Permission.is_allowed_for.and.returnValue(true);
        viewModel.attr('isNotEditable', true);

        let result = viewModel.attr('canAddUrl');

        expect(result).toBe(false);
      });

    it('returns true if user can update instance and edit is not denied', ()=> {
      Permission.is_allowed_for.and.returnValue(true);
      viewModel.attr('isNotEditable', false);

      let result = viewModel.attr('canAddUrl');

      expect(result).toBe(true);
    });
  });

  describe('canRemoveUrl get() method', ()=> {
    beforeEach(()=> {
      spyOn(Permission, 'is_allowed_for');
    });

    it('returns false if user can not update instance', ()=> {
      Permission.is_allowed_for.and.returnValue(false);

      let result = viewModel.attr('canRemoveUrl');

      expect(result).toBe(false);
    });

    it(`returns false if user can update instance 
        but edit is disabled in the component`, ()=> {
        Permission.is_allowed_for.and.returnValue(true);
        viewModel.attr('isNotEditable', true);

        let result = viewModel.attr('canRemoveUrl');

        expect(result).toBe(false);
      });

    it(`returns false if user can update instance, edit is is not denied,
        but removal is disabled by flag`, ()=> {
        Permission.is_allowed_for.and.returnValue(true);
        viewModel.attr('isNotEditable', false);
        viewModel.attr('allowToRemove', false);

        let result = viewModel.attr('canRemoveUrl');

        expect(result).toBe(false);
      });

    it(`returns true if user can update instance, edit is not denied,
        and removal is not disabled`, ()=> {
        Permission.is_allowed_for.and.returnValue(true);
        viewModel.attr('isNotEditable', false);
        viewModel.attr('allowToRemove', true);

        let result = viewModel.attr('canRemoveUrl');

        expect(result).toBe(true);
      });
  });

  describe('createUrl() method', function () {
    let method;
    let url;

    beforeEach(function () {
      method = viewModel.createUrl.bind(viewModel);
      url = 'test.url';
    });

    it('should dispatch createUrl event', function () {
      spyOn(viewModel, 'dispatch');
      method(url);
      expect(viewModel.dispatch)
        .toHaveBeenCalledWith({
          type: 'createUrl',
          payload: url,
        });
    });
  });

  describe('removeUrl() method', function () {
    let method;
    let url;

    beforeEach(function () {
      method = viewModel.removeUrl.bind(viewModel);
      url = 'test.url';
      spyOn(viewModel, 'dispatch');
    });

    it('should dispatch removeUrl event', function () {
      method(url);
      expect(viewModel.dispatch)
        .toHaveBeenCalledWith({
          type: 'removeUrl',
          payload: url,
        });
    });
  });

  describe('toggleFormVisibility() method', function () {
    let method;

    beforeEach(function () {
      method = viewModel.toggleFormVisibility.bind(viewModel);
      spyOn(viewModel, 'moveFocusToInput');
    });

    it('should set new value for form visibility', function () {
      viewModel.attr('isFormVisible', true);
      method(false);
      expect(viewModel.attr('isFormVisible')).toEqual(false);
    });

    it('should clear create url form input by default', function () {
      viewModel.attr('value', 'foobar');
      method(true);
      expect(viewModel.attr('value')).toEqual('');
    });

    it('does not clear input field value if instructed to do so', function () {
      viewModel.attr('value', 'foobar');
      method(true, true);
      expect(viewModel.attr('value')).toEqual('foobar');
    });

    it('should set focus to form input field if visible', function () {
      viewModel.attr('isFormVisible', false);
      method(true);
      expect(viewModel.moveFocusToInput).toHaveBeenCalled();
    });
  });

  describe('submitCreateUrlForm() method', function () {
    let method;

    beforeEach(function () {
      method = viewModel.submitCreateUrlForm.bind(viewModel);
      spyOn(viewModel, 'createUrl');
      spyOn(viewModel, 'toggleFormVisibility');
      spyOn(NotifiersUtils, 'notifier');
    });

    describe('in case of non-empty input', function () {
      let url;

      beforeEach(function () {
        spyOn(viewModel, 'validateUserInput').and.returnValue(true);
        url = 'test.url';
      });

      it('should validate user input', function () {
        method(url);
        expect(viewModel.validateUserInput)
          .toHaveBeenCalledWith(url);
      });

      it('prevents adding duplicate URLs', function () {
        let matches;

        viewModel.attr('urls', [
          new can.Map({link: 'www.xyz.com', title: 'www.xyz.com'}),
          new can.Map({link: 'www.bar.com', title: 'www.bar.com'}),
          new can.Map({link: 'www.baz.org', title: 'www.baz.org'}),
        ]);

        url = 'www.bar.com';
        method(url);

        matches = _.filter(viewModel.attr('urls'), {link: url});
        expect(matches.length).toEqual(1); // still only 1
        expect(viewModel.createUrl).not.toHaveBeenCalled();
      });

      it('issues error notification when adding duplicate URLs', function () {
        viewModel.attr('urls', [
          new can.Map({link: 'www.xyz.com', title: 'www.xyz.com'}),
          new can.Map({link: 'www.bar.com', title: 'www.bar.com'}),
          new can.Map({link: 'www.baz.org', title: 'www.baz.org'}),
        ]);

        method('www.bar.com');

        expect(NotifiersUtils.notifier).toHaveBeenCalledWith(
          'error', 'URL already exists.');
      });

      it('should create url', function () {
        method(url);
        expect(viewModel.createUrl)
          .toHaveBeenCalledWith(url);
      });

      it('should hide create url form', function () {
        method(url);
        expect(viewModel.toggleFormVisibility)
          .toHaveBeenCalledWith(false);
      });
    });

    describe('in case of empty input', function () {
      let url;

      beforeEach(function () {
        spyOn(viewModel, 'validateUserInput').and.returnValue(false);
        url = '   ';
      });

      it('should validate user input', function () {
        method(url);
        expect(viewModel.validateUserInput)
          .toHaveBeenCalledWith('');
      });

      it('should show create url form', function () {
        method(url);
        expect(viewModel.toggleFormVisibility)
          .toHaveBeenCalledWith(true);
      });

      it('should show notification with error message', function () {
        method(url);
        expect(NotifiersUtils.notifier).toHaveBeenCalledWith(
          'error', 'Please enter a URL.');
      });
    });
  });
});
