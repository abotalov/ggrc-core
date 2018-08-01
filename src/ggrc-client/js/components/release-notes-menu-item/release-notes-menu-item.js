/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import '../release-notes-modal/release-notes-modal';
import template from './release-notes-menu-item.mustache';
import {loadUserProfile, updateUserProfile} from '../../plugins/utils/user-utils';
import {getUtcDate} from '../../plugins/utils/date-util';

const viewModel = can.Map.extend({
  define: {
    version: {
      type: 'string',
      value: GGRC.config.VERSION,
    },
  },
  state: {
    open: false,
  },
  extraCssClass: 'release-notes',
  open(ev) {
    this.attr('state.open', true);
  },
});

const events = {
  async inserted(el) {
    let profile = await loadUserProfile();
    const lastSeenDate = getUtcDate(profile.last_seen_whats_new);
    const releaseNotesDate = getUtcDate(RELEASE_NOTES_DATE);

    if (releaseNotesDate !== lastSeenDate) {
      profile.last_seen_whats_new = releaseNotesDate;
      updateUserProfile(profile).then(() => {
        this.viewModel.open();
      });
    }
  },
};

export default can.Component.extend({
  tag: 'release-notes-menu-item',
  template,
  viewModel,
  events,
});
