/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import {ROLES_CONFLICT} from '../../events/eventTypes';
import '../custom-roles/custom-roles';
import '../custom-roles/custom-roles-modal';
import template from './templates/assessment-people.mustache';

const tag = 'assessment-people';

can.Component.extend({
  tag,
  template,
  viewModel: {
    define: {
      emptyMessage: {
        type: 'string',
        value: '',
      },
    },
    rolesConflict: false,
    infoPaneMode: true,
    instance: {},
    conflictRoles: ['Assignees', 'Verifiers'],
    orderOfRoles: ['Creators', 'Assignees', 'Verifiers'],
  },
  events: {
    [`{instance} ${ROLES_CONFLICT.type}`]: function (ev, args) {
      this.viewModel.attr('rolesConflict', args.rolesConflict);
    },
  },
});
