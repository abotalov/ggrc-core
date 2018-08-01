/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import {
  buildCountParams,
  batchRequests,
} from '../../plugins/utils/query-api-utils';
import Mappings from '../../models/mappers/mappings';

(function (can, GGRC) {
  'use strict';

  let titlesMap = {
    Total: {
      title: 'Total',
      icon: 'list-alt',
    },
    CycleTaskEntry: {
      title: 'Comments',
      icon: 'comment-o',
    },
    CycleTaskGroupObjectTask: {
      title: 'Total',
      icon: 'calendar-check-o',
    },
  };

  let viewModel = can.Map.extend({
    define: {
      icon: {
        type: 'string',
        get: function () {
          let type = this.attr('type') ? this.attr('type') : 'Total';
          let icon = titlesMap[type] ? titlesMap[type].icon : type;

          return icon.toLowerCase();
        },
      },
      title: {
        type: 'string',
        get: function () {
          let title = this.attr('type') ? this.attr('type') : 'Total';

          return titlesMap[title] ? titlesMap[title].title : title;
        },
      },
    },
    instance: null,
    type: '@',
    count: 0,
    load: function () {
      let instance = this.attr('instance');
      let type = this.attr('type');
      let relevant = {
        id: instance.id,
        type: instance.type,
      };
      let types = type ? [type] : Mappings.getMappingList(instance.type);
      let countQuery = buildCountParams(types, relevant);
      let dfds = countQuery.map(batchRequests);

      return $.when(...dfds).then(function () {
        let counts = Array.prototype.slice.call(arguments);

        let total = types.reduce(function (count, type, ind) {
          return count + counts[ind][type].total;
        }, 0);

        this.attr('count', total);
      }.bind(this));
    },
  });

  GGRC.Components('mappedCounter', {
    tag: 'mapped-counter',
    template: '<i class="fa fa-{{icon}}"></i> {{title}}: {{count}}',
    viewModel: viewModel,
    events: {
      inserted: function () {
        let vm = this.viewModel;
        let promise = vm.load();

        if (vm.addContent) {
          vm.addContent(promise);
        }
      },
    },
  });
})(window.can, window.GGRC);
