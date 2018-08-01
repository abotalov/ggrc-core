/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import ModalsController from './modals_controller';
import pubsub from '../../pub-sub';
import {notifier} from '../../plugins/utils/notifiers-utils';

export default ModalsController({
  pluginName: 'ggrc_controllers_delete',
  defaults: {
    skip_refresh: true,
  },
}, {
  init: function () {
    this._super();
  },
  '{$footer} a.btn[data-toggle=delete]:not(:disabled) click'(el, ev) {
    let that = this;
    // Disable the cancel button.
    let cancelButton = this.element.find('a.btn[data-dismiss=modal]');
    let modalBackdrop = this.element.data('modal_form').$backdrop;

    this.bindXHRToButton(this.options.instance.refresh()
      .then(function (instance) {
        return instance.destroy();
      }).then(function (instance) {
        // If this modal is spawned from an edit modal, make sure that one does
        // not refresh the instance post-delete.
        let parentController = $(that.options.$trigger)
          .closest('.modal').control();
        let msg;
        if (parentController) {
          parentController.options.skip_refresh = true;
        }

        msg = instance.display_name() + ' deleted successfully';
        $(document.body).trigger('ajax:flash', {success: msg});
        if (that.element) {
          that.element.trigger('modal:success', that.options.instance);
        }

        pubsub.dispatch({
          type: 'objectDeleted',
          instance,
        });

        return new $.Deferred(); // on success, just let the modal be destroyed or navigation happen.
        // Do not re-enable the form elements.
      }).fail(function (xhr, status) {
        let message = xhr.responseJSON;

        if (xhr.responseJSON && xhr.responseJSON.message) {
          message = xhr.responseJSON.message;
        }

        notifier('error', message);
      }), el.add(cancelButton).add(modalBackdrop));
  },
});
