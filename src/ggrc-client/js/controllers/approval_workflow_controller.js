/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import {getPageInstance} from '../plugins/utils/current-page-utils';

;(function (can, $, GGRC, CMS) {
  GGRC.register_modal_hook('approvalform', function ($target, $trigger, option) {
    let instance;
    let object_params = JSON.parse($trigger.attr('data-object-params') || '{}');

    if($trigger.attr('data-object-id') === 'page') {
      instance = getPageInstance();
    } else {
      instance = CMS.Models.get_instance(
        $trigger.data('object-singular'),
        $trigger.attr('data-object-id')
      );
    }

    $target
      .modal_form(option, $trigger)
      .ggrc_controllers_approval_workflow({
        object_params: object_params,
        current_user: GGRC.current_user,
        instance: instance,
      });
  });

})(window.can, window.can.$, window.GGRC, window.CMS);


// Calendar authentication

jQuery(function ($){
  $('body').on('click', '.calendar-auth', function (e) {
    let calenderAuthWin = null;
    let href = window.location.origin + '/calendar_oauth_request'; // "https://ggrc-dev.googleplex.com/calendar_oauth_request"
    let name = 'Calendar Authentication';

    if(calenderAuthWin === null || calenderAuthWin.closed){
      calenderAuthWin = window.open(href, name);
      calenderAuthWin.focus();
    }
    else{
      calenderAuthWin.focus();
    }
  });
});
