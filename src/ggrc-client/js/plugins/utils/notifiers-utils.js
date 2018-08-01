/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

const messages = {
  'default': 'There was an error!',
  '401': 'The server says you are not authorized. Are you logged in?',
  '403': 'You don\'t have the permission to access the ' +
  'requested resource. It is either read-protected or not ' +
  'readable by the server.',
  '409': 'There was a conflict while saving.' +
  ' Your changes have not been saved yet.' +
  ' Please refresh the page and try saving again',
  '412': 'One of the form fields isn\'t right. ' +
  'Check the form for any highlighted fields.',
};

/**
 * Shows flash notification
 * @param  {String} type    type of notification. error|warning
 * @param  {String} message Plain text message or mustache template if data is passed
 * @param  {Object} [data] data to populate mustache template
 */
function notifier(type, message, data) {
  let props = {};

  if ( message && data ) {
    message = can.mustache(message);
    props.data = data;
  }

  type = type || 'warning';
  props[type] = message || messages.default;
  $('body').trigger('ajax:flash', props);
}

function notifierXHR(type, message) {
  return function (err) {
    let status = err && err.status ? err.status : null;

    if (status && !message) {
      message = messages[status];
    }

    notifier(type, message);
  };
}

window.addEventListener('error', (event) => {
  notifier('error', event.message);
});

export {
  messages,
  notifier,
  notifierXHR,
};
