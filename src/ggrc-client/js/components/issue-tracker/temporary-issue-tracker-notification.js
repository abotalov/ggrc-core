/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import {notifier} from '../../plugins/utils/notifiers-utils';

// Temporary BA solution. User can't edit TICKET TRACKER params only from GGRC.
// Changes are save in GGRC, but hotlist isn't removed in issue tracker issue.
// So this message will be showing till bug not fixed on BE.

export const showTrackerNotification = () => {
  const message = `To change or remove hotlist,
  you have to remove it for Assessment and then
  make necessary changes in Issue Tracker.
  Sorry for inconvenience.`;

  notifier('notify', message);
};
