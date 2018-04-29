/*
  Copyright (C) 2018 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import {
  uploadFiles,
} from '../../plugins/utils/gdrive-picker-utils';
import {
  confirm,
} from '../../plugins/utils/modals';
import {
  BEFORE_DOCUMENT_CREATE,
  DOCUMENT_CREATE_FAILED,
} from '../../events/eventTypes';
import template from './create-document-button.mustache';

const viewModel = can.Map.extend({
  parentInstance: null,
  getDocument(file) {
    return this.checkDocumentExists(file)
      .then((documentStatus) => {
        if (documentStatus.status === 'exists') {
          return this.useExistingDocument(documentStatus.document);
        } else {
          return this.createDocument(file);
        }
      });
  },
  checkDocumentExists(file) {
    return $.post('/api/is_document_with_gdrive_id_exists', {
      gdrive_id: file.id,
    });
  },
  useExistingDocument(document) {
    return this.showConfirm()
      .then(() => {
        return new CMS.Models.Document(document);
      });
  },
  createDocument(file) {
    this.attr('parentInstance').dispatch(BEFORE_DOCUMENT_CREATE);

    let instance = new CMS.Models.Document({
      title: file.title,
      source_gdrive_id: file.id,
      created_at: Date.now(),
      context: {id: null},
    });

    return instance.save()
      .then((doc) => {
        return doc;
      }, () => {
        this.attr('parentInstance').dispatch(DOCUMENT_CREATE_FAILED);
      });
  },
  showConfirm() {
    let confirmation = can.Deferred();
    let parentInstance = this.attr('parentInstance');
    confirm({
      modal_title: 'Warning',
      modal_description: `This gDrive file is already mapped to GGRC. </br></br>
        Please proceed to map existing doc to
        "${parentInstance.type} ${parentInstance.title}"`,
      button_view:
        `${GGRC.mustache_path}/modals/confirm_cancel_buttons.mustache`,
      modal_confirm: 'Proceed',
    }, confirmation.resolve, confirmation.reject);

    return confirmation;
  },
});

export default can.Component.extend({
  tag: 'create-document-button',
  template,
  viewModel,
  events: {
    '.pick-file click'() {
      uploadFiles()
        .then((files) => {
          let file = files[0];
          this.attach(file);
        }, () => {
          // event handler in object-mapper will open mapper again
          $(window).trigger('modal:dismiss');
        });
    },
    attach(file) {
      this.viewModel.getDocument(file)
        .then((document) => {
          this.element.trigger('modal:success', [document]);
        })
        .always(() => {
          // handler in object-mapper will close mapper permanently
          // and remove html from the dom
          this.element.trigger('modal:dismiss');
        });
    },
  },
});
