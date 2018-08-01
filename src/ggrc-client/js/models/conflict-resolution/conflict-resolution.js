/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import {
  simpleFieldResolver,
  customAttributeResolver,
  objectListResolver,
} from './conflict-resolvers';
import {messages} from '../../plugins/utils/notifiers-utils';

export function checkValues(baseAttrs, attrs, remoteAttrs, obj) {
  let hasConflict = false;

  Object.keys(baseAttrs).forEach((key) => {
    let unableToResolve = false;

    switch (key) {
      // We skip the updated_at key because we know it has changed
      case 'updated_at':
        break;
      // We have a special way for customAttributes because it is nested field
      case 'custom_attribute_values':
        unableToResolve = customAttributeResolver(
          baseAttrs[key],
          attrs[key],
          remoteAttrs[key],
          obj.attr(key));
        break;
      case 'assertions':
      case 'categories':
        unableToResolve = objectListResolver(
          baseAttrs[key],
          attrs[key],
          remoteAttrs[key],
          obj.attr(key));
        break;
      default:
        unableToResolve = simpleFieldResolver(
          baseAttrs,
          attrs,
          remoteAttrs,
          obj,
          key);
    }

    hasConflict = hasConflict || unableToResolve;
  });

  return hasConflict;
}

export default function resolveConflict(xhr, obj) {
  let attrs = can.extend(true, {}, obj.attr());
  let baseAttrs = can.extend(true, {}, obj._backupStore()) || {};
  return obj.refresh().then(function (obj) {
    let conflict = false;
    let remoteAttrs = can.extend(true, {}, obj.attr());

    if (can.Object.same(remoteAttrs, attrs)) {
      // current state is same as server state -- do nothing.
      return obj;
    } else if (can.Object.same(remoteAttrs, baseAttrs)) {
      // base state matches server state -- no incorrect expectations -- save.
      return obj.attr(attrs).save();
    }
    // check what properties changed -- we can merge if the same prop wasn't changed on both
    conflict = checkValues(baseAttrs, attrs, remoteAttrs, obj);
    if (conflict) {
      $(document.body).trigger('ajax:flash', {
        warning: messages[409],
      });
      xhr.remoteObject = remoteAttrs;
      return new $.Deferred().reject(xhr, 409, 'CONFLICT');
    }
    return obj.save();
  });
}
