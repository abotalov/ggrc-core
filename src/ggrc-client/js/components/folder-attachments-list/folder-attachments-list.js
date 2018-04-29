/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import '../object-list-item/editable-document-object-list-item';
import {
  BEFORE_MAPPING,
  REFRESH_MAPPING,
  BEFORE_DOCUMENT_CREATE,
  DOCUMENT_CREATE_FAILED,
} from '../../events/eventTypes';
import template from './folder-attachments-list.mustache';

/**
 * Wrapper Component for rendering and managing of folder and
 * attachments lists
 */
export default can.Component.extend({
  tag: 'folder-attachments-list',
  template: template,
  viewModel: {
    define: {
      showSpinner: {
        type: 'boolean',
        get() {
          return this.attr('isUnmapping')
            || this.attr('isListLoading')
            || this.attr('isMapping');
        },
      },
    },
    readonly: false,
    title: null,
    tooltip: null,
    instance: null,
    folderError: null,
    isAttaching: false,
    isUnmapping: false,
    isListLoading: false,
  },
  events: {
    [`{viewModel.instance} ${BEFORE_DOCUMENT_CREATE.type}`]() {
      this.viewModel.attr('isMapping', true);
    },
    [`{viewModel.instance} ${DOCUMENT_CREATE_FAILED.type}`]() {
      this.viewModel.attr('isMapping', false);
    },
    [`{viewModel.instance} ${BEFORE_MAPPING.type}`](scope, ev) {
      if (ev.destinationType === 'Document') {
        this.viewModel.attr('isMapping', true);
      }
    },
    [`{viewModel.instance} ${REFRESH_MAPPING.type}`]() {
      this.viewModel.attr('isMapping', false);
    },
  },
});
