/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import ModalsController from './modals_controller';

export default ModalsController({
  pluginName: 'ggrc_controllers_quick_form',
  defaults: {
    model: null,
    instance: null,
  },
}, {
  init: function () {
    if (this.options.instance && !this.options.model) {
      this.options.model = this.options.instance.constructor;
    }
    this.options.$content = this.element;
  },
});
