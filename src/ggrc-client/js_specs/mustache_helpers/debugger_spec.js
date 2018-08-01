/*
  Copyright (C) 2018 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

describe('can.mustache.helper.debugger', function () {
  let fakeOptions;
  let helper;

  beforeAll(function () {
    fakeOptions = {
      fn: jasmine.createSpy(),
    };

    helper = can.Mustache._helpers['debugger'].fn;
  });

  it('does not throw an error when called with more than one argument',
    function () {
      try {
        helper(1, 'foo', ['bar'], fakeOptions);
      } catch (ex) {
        fail('Helper threw an error: ' + ex.message);
      }
    }
  );

});
