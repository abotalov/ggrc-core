/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

function cacheCurrentUser() {
  CMS.Models.Person.model(GGRC.current_user);
}

let profilePromise;

function loadUserProfile() {
  if (typeof profilePromise === 'undefined') {
    profilePromise = can.ajax({
      type: 'GET',
      headers: $.extend({
        'Content-Type': 'application/json',
      }, {}),
      url: '/api/people/' + GGRC.current_user.id + '/profile',
    });
  }

  return profilePromise;
}

function updateUserProfile(profile) {
  let result = can.ajax({
    type: 'PUT',
    headers: $.extend({
      'Content-Type': 'application/json',
    }, {}),
    url: '/api/people/' + GGRC.current_user.id + '/profile',
    data: profile,
  });

  result.then(() => {
    profilePromise = undefined;
  });

  return result;
}

export {
  cacheCurrentUser,
  loadUserProfile,
  updateUserProfile,
};
