/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

(function (GGRC, can) {
  GGRC.ListLoaders.BaseListLoader('GGRC.ListLoaders.CrossListLoader', {}, {
    init: function (localMapping, remoteMapping) {
      this._super();

      this.local_mapping = localMapping;
      this.remote_mapping = remoteMapping;
    },
    init_listeners: function (binding) {
      if (!binding.bound_insert_from_source_binding) {
        binding.bound_insert_from_source_binding =
          this.proxy('insert_from_source_binding', binding);
        binding.bound_remove_from_source_binding =
          this.proxy('remove_from_source_binding', binding);
      }

      binding.source_binding = binding.instance.get_binding(this.local_mapping);

      binding.source_binding.list.bind(
        'add', binding.bound_insert_from_source_binding);
      binding.source_binding.list.bind(
        'remove', binding.bound_remove_from_source_binding);
    },
    insert_from_source_binding: function (binding, ev, localResults, index) {
      let self = this;
      can.each(localResults, function (localResult) {
        // FIXME: This is identical to code in _refresh_stubs
        let remoteBinding = self.insert_local_result(binding, localResult);
        remoteBinding.refresh_instance().then(function () {
          remoteBinding.refresh_stubs();
        });
      });
    },
    remove_from_source_binding: function (binding, ev, localResults, index) {
      let self = this;
      can.each(localResults, function (localResult) {
        self.remove_local_result(binding, localResult);
      });
    },
    insert_local_result: function (binding, localResult) {
      let self = this;
      let i;
      let localResults;
      let remoteBinding;

      if (!binding.remote_bindings)
        binding.remote_bindings = [];

      for (i = 0; i < binding.remote_bindings.length; i++) {
        if (binding.remote_bindings[i].instance === localResult.instance)
          return binding.remote_bindings[i];
      }

      remoteBinding =
        localResult.instance.get_binding(self.remote_mapping);
      remoteBinding.bound_insert_from_remote_binding =
        this.proxy('insert_from_remote_binding', binding, remoteBinding);
      remoteBinding.bound_remove_from_remote_binding =
        this.proxy('remove_from_remote_binding', binding, remoteBinding);

      binding.remote_bindings.push(remoteBinding);

      remoteBinding.list.bind(
        'add', remoteBinding.bound_insert_from_remote_binding);
      remoteBinding.list.bind(
        'remove', remoteBinding.bound_remove_from_remote_binding);

      localResults = can.map(remoteBinding.list, function (result) {
        return self.make_result(result.instance, [result], binding);
      });
      self.insert_results(binding, localResults);

      return remoteBinding;
    },
    remove_local_result: function (binding, localResult) {
      let self = this;
      let remoteBinding;
      let i;
      let remoteBindingIndex;

      if (!binding.remote_bindings)
        binding.remote_bindings = [];

      for (i = 0; i < binding.remote_bindings.length; i++) {
        if (binding.remote_bindings[i].instance === localResult.instance)
          remoteBinding = binding.remote_bindings[i];
      }

      if (!remoteBinding) {
        console.debug('Removed binding not found:', localResult, binding);
        return;
      }

      remoteBinding.list.unbind(
        'add', remoteBinding.bound_insert_from_remote_binding);
      remoteBinding.list.unbind(
        'remove', remoteBinding.bound_remove_from_remote_binding);

      can.each(remoteBinding.list, function (result) {
        self.remove_instance(binding, result.instance, result);
      });

      remoteBindingIndex = binding.remote_bindings.indexOf(remoteBinding);
      binding.remote_bindings.splice(remoteBindingIndex, 1);
    },
    insert_from_remote_binding: function (binding, remoteBinding, ev, results) {
      let self = this;
      let newResults = can.map(results, function (result) {
        return self.make_result(result.instance, [result], binding);
      });
      this.insert_results(binding, newResults);
    },
    remove_from_remote_binding: function (binding, remoteBinding, ev, results) {
      let self = this;
      can.each(results, function (result) {
        self.remove_instance(binding, result.instance, result);
      });
    },
    _refresh_stubs: function (binding) {
      let self = this;

      return binding.source_binding.refresh_stubs()
        .then(function (localResults) {
          let deferreds = [];

          can.each(localResults, function (localResult) {
            let remoteBinding = self.insert_local_result(binding, localResult);
            let deferred = remoteBinding.refresh_instance().then(function () {
              return remoteBinding.refresh_stubs();
            });

            deferreds.push(deferred);
          });

          return $.when(...deferreds);
        })
        .then(function () {
          return binding.list;
        });
    },
  });
})(window.GGRC, window.can);
