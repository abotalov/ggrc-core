/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import {makeFakeInstance} from '../../../../js_specs/spec_helpers';
import Relationship from '../relationship'

describe('Relationship model', function () {
  describe('unmap() method', function () {
    let instance;

    beforeEach(function () {
      instance = makeFakeInstance({model: Relationship})({
        id: 'testId',
      });
    });

    it('sends correct request if not cascade', function () {
      spyOn($, 'ajax').and.returnValue(jasmine.createSpyObj(['done']));

      instance.unmap(false);

      expect($.ajax).toHaveBeenCalledWith({
        type: 'DELETE',
        url: '/api/relationships/testId?cascade=false',
      });
    });

    it('sends correct request if cascade', function () {
      spyOn($, 'ajax').and.returnValue(jasmine.createSpyObj(['done']));

      instance.unmap(true);

      expect($.ajax).toHaveBeenCalledWith({
        type: 'DELETE',
        url: '/api/relationships/testId?cascade=true',
      });
    });

    it('triggers "destroyed" event', function () {
      spyOn($, 'ajax').and.returnValue(can.Deferred().resolve());
      spyOn(can, 'trigger');

      instance.unmap(true);

      expect(can.trigger)
        .toHaveBeenCalledWith(instance.constructor, 'destroyed', instance);
    });
  });
});
