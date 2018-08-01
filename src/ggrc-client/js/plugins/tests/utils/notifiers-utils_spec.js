/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import {
  notifier,
  notifierXHR,
  messages,
} from './../../utils/notifiers-utils';

describe('notifiers-utils module', function () {
  let trigger;
  let _originalMessages;

  beforeAll(function () {
    _originalMessages = {
      'default': messages['default'],
      '401': messages['401'],
    };

    messages['default'] = 'Some error!';
    messages['401'] = 'Mock auth invalid message';

    trigger = spyOn($.prototype, 'trigger');
  });

  afterAll(function () {
    Object.assign(messages, _originalMessages);
  });

  describe('notifier method', function () {
    describe('returns default message', function () {
      describe('and warning type', function () {
        it('if all parameters empty', function () {
          notifier();
          expect(trigger).toHaveBeenCalledWith('ajax:flash',
            {warning: 'Some error!'});
        });
      });

      describe('and error type', function () {
        it('and error type', function () {
          notifier('error');

          expect(trigger).toHaveBeenCalledWith('ajax:flash',
            {error: 'Some error!'});
        });
      });
    });
  });

  describe('notifierXHR method', function () {
    describe('returns default message', function () {
      describe('and warning type', function () {
        it('for unknown errors', function () {
          notifierXHR()({status: 666});

          expect(trigger).toHaveBeenCalledWith('ajax:flash',
            {warning: 'Some error!'});
        });
      });

      describe('and error type', function () {
        it('for unknown errors', function () {
          notifierXHR('error')({status: 666});

          expect(trigger).toHaveBeenCalledWith('ajax:flash',
            {error: 'Some error!'});
        });
      });
    });

    describe('returns standard message by error code', function () {
      it('for 401 status', function () {
        notifierXHR('error')({status: 401});

        expect(trigger).toHaveBeenCalledWith('ajax:flash',
          {error: 'Mock auth invalid message'});
      });
    });

    describe('returns passed message', function () {
      it('for defined error statuses', function () {
        notifierXHR('error', 'Fake message')({status: 403});

        expect(trigger).toHaveBeenCalledWith('ajax:flash',
          {error: 'Fake message'});
      });
    });
  });
});
