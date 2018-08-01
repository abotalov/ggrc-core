/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import {SWITCH_TO_ERROR_PANEL, SHOW_INVALID_FIELD} from '../../events/eventTypes';
import template from './object-state-toolbar.mustache';

const tag = 'object-state-toolbar';
const activeStates = ['In Progress', 'Rework Needed', 'Not Started'];
// Helper function - might be some util/helpers method
function checkIsCurrentUserVerifier(verifiers) {
  return verifiers
    .filter(function (verifier) {
      return verifier.id === GGRC.current_user.id;
    }).length;
}
/**
 * Object State Toolbar Component allowing Object state modification
 */
export default can.Component.extend({
  tag,
  template,
  viewModel: {
    define: {
      updateState: {
        get: function () {
          return this.attr('hasVerifiers') ? 'In Review' : 'Completed';
        },
      },
      isCurrentUserVerifier: {
        get: function () {
          return checkIsCurrentUserVerifier(this.attr('verifiers'));
        },
      },
      hasVerifiers: {
        get: function () {
          return this.attr('verifiers').length;
        },
      },
    },
    disabled: false,
    verifiers: [],
    instance: {},
    isActiveState: function () {
      return activeStates.includes(this.attr('instance.status'));
    },
    isInProgress: function () {
      return this.attr('instance.status') === 'In Progress';
    },
    isInReview: function () {
      return this.attr('instance.status') === 'In Review';
    },
    hasPreviousState: function () {
      return !!this.attr('instance.previousStatus');
    },
    changeState: function (newState, isUndo) {
      if (this.attr('instance._hasValidationErrors')) {
        this.attr('instance').dispatch(SWITCH_TO_ERROR_PANEL);
        this.attr('instance').dispatch(SHOW_INVALID_FIELD);
        return;
      }

      newState = newState || this.attr('updateState');
      this.dispatch({
        type: 'onStateChange',
        state: newState,
        undo: isUndo,
      });
    },
  },
});
