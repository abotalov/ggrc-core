/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

(function (can, $) {
  /*
    This component is for quickly updating the properties of an object through form fields.
    It works similar to GGRC.Controllers.QuickForm but has an extra feature: if the instance
    we're working with is a join object, and the option type is changed, it will work around
    the lack of support in proxy mappers for join objects being changed like that, and
    destroy the join object while creating a new one.

    Field updates trigger updates to the model automatically, even on the server.  This differs
    from the quick-add component above, in that it is not waiting for a submit trigger.
  */
  can.Component.extend({
    tag: 'ggrc-quick-update',
    template: '<content/>',
    scope: {
      instance: null,
      source_mapping: null,
      model: null,
      attributes: {},
    },
    events: {
      init: function () {
        this.scope.attr('controller', this);
        this.scope.attr('model', this.scope.model || this.scope.instance.constructor);
        if(!this.scope.instance._transient) {
          // only refresh if there's not currently an edit modal spawned.
          this.scope.instance.refresh();
        }
      },
      // currently we don't support proxy object updates in mappings, so for now a change
      // to a connected object (assuming we are operating on a proxy object) will trigger
      // a deletion of the proxy object and creation of a new one.
      autocomplete_select: function (el, event, ui) {
        let that = this;
        setTimeout(function () {
          let serial = that.scope.instance.serialize();
          delete serial[el.attr('name')];
          delete serial[el.attr('name') + '_id'];
          delete serial[el.attr('name') + '_type'];
          delete serial.id;
          delete serial.href;
          delete serial.selfLink;
          delete serial.created_at;
          delete serial.updated_at;
          delete serial.provisional_id;
          serial[el.attr('name')] = ui.item.stub();
          that.scope.instance.destroy().then(function () {
            new that.scope.model(serial).save();
          });
        });
      },
      // null-if-empty attributes are a pattern carried over from GGRC.Controllers.Modals
      // Useful for connected objects.
      'input[null-if-empty] change': function (el) {
        if (!el.val()) {
          this.scope.instance.attr(el.attr('name'), null);
        }
      },
      'input, select change': function (el) {
        let isCheckbox = el.is('[type=checkbox][multiple]');
        let isDropdown = el.is('select');
        if (isCheckbox) {
          if (!this.scope.instance[el.attr('name')]) {
            this.scope.instance.attr(el.attr('name'), new can.List());
          }
          this.scope.instance
            .attr(el.attr('name'))
            .replace(
              can.map(
                this.element.find("input[name='" + el.attr('name') + "']:checked"),
                function (el) {
                  return $(el).val();
                }
              )
            );
          this.element.find('input:checkbox').prop('disabled', true);
        } else {
          this.scope.instance.attr(el.attr('name'), el.val());
          if (isDropdown) {
            el.closest('dropdown').attr('is-disabled', true);
          }
        }
        this.scope.instance.save().then(function () {
          if (isCheckbox) {
            this.element.find('input:checkbox').prop('disabled', false);
          } else if (isDropdown) {
            el.closest('dropdown').attr('is-disabled', false);
          }
        }.bind(this));
      },
    },
  });
})(window.can, window.can.$);
