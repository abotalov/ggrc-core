/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import RefreshQueue from '../refresh_queue';

(function (GGRC, can) {
  can.Construct('GGRC.ListLoaders.BaseListLoader', {
    binding_factory: function (instance, loader) {
      return new GGRC.ListLoaders.ListBinding(instance, loader);
    },
  }, {
    init: function () {
    },

    attach: function (instance) {
      let binding = this.constructor.binding_factory(instance, this);
      this.init_listeners(binding);
      return binding;
    },

    make_result: function (instance, mappings, binding) {
      return new GGRC.ListLoaders.MappingResult(instance, mappings, binding);
    },

    find_result_by_instance: function (result, list) {
      let i;
      let foundResult = null;
      let oldResult;

      for (i = 0; !foundResult && i < list.length; i++) {
        oldResult = list[i];
        if (oldResult.instance.id === result.instance.id &&
          oldResult.instance.constructor.shortName ===
          result.instance.constructor.shortName) {
          foundResult = oldResult;
        }
      }

      return foundResult;
    },

    is_duplicate_result: function (oldResult, newResult) {
      let old = oldResult;
      let new_ = newResult;

      if (old.instance === new_.instance) {// && o.binding  === n.binding) {
        if (old.mappings === new_.mappings) {
          return true;
        }
        old = old.mappings;
        new_ = new_.mappings;
        if (old && new_ && old.length === 1 && new_.length === 1) {
          old = old[0];
          new_ = new_[0];
          if (old.binding === new_.binding) {
            if (old.instance === new_.instance &&
              (old.mappings.length > 0 || new_.mappings.length > 0)) {
              old = old.mappings;
              new_ = new_.mappings;
              if (old && new_ && old.length === 1 && new_.length === 1) {
                old = old[0];
                new_ = new_[0];
              }
            }

            if (old.binding === new_.binding && old.instance === true &&
              new_.instance === true && old.mappings &&
              old.mappings.length === 0 && new_.mappings &&
              new_.mappings.length === 0) {
              return true;
            }
          }
        }
      }

      return false;
    },

    insert_results: function (binding, results) {
      let self = this;
      let allBindingResults = [];
      let newInstanceResults = [];
      let instancesToRefresh = [];

      can.each(results, function (newResult) {
        let foundResult = null;
        let mappingAttr;

        foundResult = self.find_result_by_instance(newResult, binding.list);

        if (!foundResult && binding.pending_list) {
          foundResult =
            self.find_result_by_instance(newResult, binding.pending_list);
        }

        if (!foundResult) {
          foundResult =
            self.find_result_by_instance(newResult, newInstanceResults);
        }

        if (foundResult) {
          if (self.is_duplicate_result(foundResult, newResult)) {
            return;
          }

          mappingAttr = foundResult.mappings;
          // Since we're adding the result as its own mapping, use
          // new_result as the mapping instead of new_result.mappings?

          can.each(newResult.mappings, function (mapping) {
            // TODO: Examine when this will be false -- is it a sign of
            //   duplicate work?
            if (mappingAttr.indexOf && mappingAttr.indexOf(mapping) === -1) {
              foundResult.insert_mapping(mapping);
              instancesToRefresh.push(newResult.instance);
            }
          });

          allBindingResults.push(foundResult);
        } else {
          //  FIXME: Loaders should be passing in newly instantiated results,
          //    so this line should be:
          //      found_result = new_result;
          //    but it's not a big deal
          foundResult =
            self.make_result(newResult.instance, newResult.mappings, binding);
          newInstanceResults.push(foundResult);
          instancesToRefresh.push(newResult.instance);
          // FIXME: Also queue mappings to refresh?

          allBindingResults.push(foundResult);
        }
      });

      if (newInstanceResults.length > 0) {
        binding.list.push(...newInstanceResults);

        //  TODO: Examine whether deferring this list insertion avoids
        //    causing client-side freezes
        /* if (!binding.pending_list)
         binding.pending_list = [];
         binding.pending_list.push.apply(binding.pending_list, new_instance_results);

         if (!binding.pending_timeout) {
         binding.pending_deferred = new $.Deferred();
         binding.pending_timeout = setTimeout(function() {
         binding.list.push.apply(binding.list, binding.pending_list);
         delete binding.pending_list;
         delete binding.pending_timeout;
         binding.pending_deferred.resolve();
         delete binding.pending_deferred;
         }, 100);
         }*/
      }

      return allBindingResults;
    },

    remove_instance: function (binding, instance, mappings) {
      let indexesToRemove = [];

      if (!(can.isArray(mappings) || mappings instanceof can.Observe.List))
        mappings = [mappings];

      can.each(binding.list, function (data, instanceIndex) {
        let mappingAttr = binding.list[instanceIndex].mappings;

        if (data.instance.id === instance.id &&
          data.instance.constructor.shortName ===
          instance.constructor.shortName) {
          if (mappingAttr.length === 0) {
            indexesToRemove.push(instanceIndex);
          } else {
            can.each(mappings, function (mapping) {
              let wasRemoved = data.remove_mapping(mapping);
              if (wasRemoved) {
                if (mappingAttr.length === 0)
                  indexesToRemove.push(instanceIndex);
              }
            });
          }
        }
      });
      can.each(indexesToRemove.sort(), function (indexToRemove, count) {
        binding.list.splice(indexToRemove - count, 1);
      });
    },

    refresh_stubs: function (binding) {
      if (!binding._refresh_stubs_deferred) {
        binding._refresh_stubs_deferred = $.when(this._refresh_stubs(binding));
      }
      return binding._refresh_stubs_deferred
        .then(function () {
          return binding.list;
        });
    },

    refresh_instances: function (binding, force) {
      if (force || !binding._refresh_instances_deferred) {
        binding._refresh_instances_deferred =
          $.when(this._refresh_instances(binding, force));
      }
      return binding._refresh_instances_deferred
        .then(
          function () {
            return binding.list;
          },
          function () {
            setTimeout(function () {
              delete binding._refresh_instances_deferred;
            }, 10);
            return this;
          });
    },

    _refresh_instances: function (binding, force) {
      return this.refresh_stubs(binding)
        .then(function () {
          let refreshQueue = new RefreshQueue();
          can.each(binding.list, function (result) {
            refreshQueue.enqueue(result.instance, force);
          });
          return refreshQueue.trigger();
        });
    },
  });
})(window.GGRC, window.can);
