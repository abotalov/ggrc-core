/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

 import Relationship from '../join-models/relationship';

(function (GGRC, can) {
  GGRC.ListLoaders.StubFilteredListLoader(
    'GGRC.ListLoaders.AttrFilteredListLoader', {}, {
      init: function (source, prop, value, type) {
        let filterFn = function (binding) {
          // TODO: We should filter by type as well
          if (!binding.mappings) {
            return;
          }
          return _.any(binding.mappings, function (mapping) {
            let instance = mapping.instance;
            if (instance instanceof Relationship) {
              if (_.exists(instance, 'attrs') &&
                  instance.attrs[prop] && (!value ||
                _.contains(instance.attrs[prop].split(','), value))) {
                return true;
              }
            }
            return filterFn(mapping);
          });
        };
        this.prop_name = prop;
        this.keyword = value;
        this.object_type = type;
        this._super(source, filterFn);
      },
      init_listeners: function (binding) {
        this._super(binding);
        function itemFromList(list, id) {
          return _.first(can.makeArray(list).filter(function (item) {
            return item.instance.id === id;
          }));
        }

        Relationship.bind('updated', function (ev, model) {
          let value;
          let needle;
          let active;
          let activeInList;
          let contains;
          if (!(model instanceof Relationship)) {
            return;
          }
          value = can.getObject('attrs.' + this.prop_name, model);

          if (model.source.type === this.object_type) {
            needle = model.source;
          } else if (model.destination.type === this.object_type) {
            needle = model.destination;
          }
          if (!needle || !value) {
            return;
          }
          active = itemFromList(binding.source_binding.list, needle.id);
          activeInList = itemFromList(binding.list, needle.id);

          if (!active) {
            return;
          }
          contains = _.contains(value.split(','), this.keyword);
          if (!contains && activeInList) {
            binding.list.splice(
              _.map(binding.list, function (e) {
                return e.instance.id;
              }).indexOf(active.instance.id),
              1
            );
          }
          if (contains && !activeInList) {
            this.insert_results(binding, [active]);
          }
        }.bind(this));
      },
    });
})(window.GGRC, window.can);
