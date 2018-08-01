/*
  Copyright (C) 2018 Google Inc., authors, and contributors <see AUTHORS file>
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import {
  peopleWithRoleName,
} from '../../plugins/utils/acl-utils';
import './inline-aggregate-field';

const viewModel = can.Map.extend({
  define: {
    peopleList: {
      get() {
        const instance = this.attr('instance');
        const roleName = this.attr('role');
        return peopleWithRoleName(instance, roleName);
      },
    },
  },
  instance: {},
  role: '',
});

export default can.Component.extend('peopleWithRoleInlineField', {
  tag: 'people-with-role-inline-field',
  template: `<inline-aggregate-field {source}="peopleList"
    {field}="'email'"/>`,
  viewModel,
});
