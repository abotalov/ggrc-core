/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from './people-list-info.mustache';
import '../../models/service-models/role';

(function (can, GGRC) {
  'use strict';

  let viewModel = can.Map.extend({
    instance: null,
    isOpen: false,
    isHidden: false,
    isRefreshed: false,
    isAttributesDisabled: false,
    refreshInstance() {
      if (this.attr('isRefreshed')) {
        return;
      }

      this.attr('isAttributesDisabled', true);
      this.attr('instance').refresh().then(() => {
        this.attr('isAttributesDisabled', false);
      });
      this.attr('isRefreshed', true);
    },
  });

  GGRC.Components('peopleListInfo', {
    tag: 'people-list-info',
    template: template,
    viewModel: viewModel,
    events: {
      ' open'() {
        this.viewModel.attr('isHidden', false);
        this.viewModel.attr('isOpen', true);
        this.viewModel.refreshInstance();
      },
      ' close'() {
        this.viewModel.attr('isHidden', true);
      },
    },
  });
})(window.can, window.GGRC);
