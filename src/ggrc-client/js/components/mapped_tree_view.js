/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import './object-list-item/editable-document-object-list-item';
import {notifierXHR} from '../plugins/utils/notifiers-utils';

(function (can, $) {
  GGRC.Components('mappingTreeView', {
    tag: 'mapping-tree-view',
    template: can.view(GGRC.mustache_path +
      '/base_templates/mapping_tree_view.mustache'),
    scope: {
      treeViewClass: '@',
      expandable: '@',
      sortField: '@',
      sortOrder: '@',
      emptyText: '@',
      parentInstance: null,
      mappedObjects: [],
      isExpandable: function () {
        let expandable = this.attr('expandable');
        if (expandable === null || expandable === undefined) {
          return true;
        } else if (typeof expandable === 'string') {
          return expandable === 'true';
        }
        return expandable;
      },
    },
    init: function (element) {
      let el = $(element);
      let binding;

      _.each(['mapping', 'itemTemplate'], function (prop) {
        if (!this.scope.attr(prop)) {
          this.scope.attr(prop,
            el.attr(can.camelCaseToDashCase(prop)));
        }
      }, this);

      binding = this.scope.parentInstance.get_binding(this.scope.mapping);

      binding.refresh_instances().then(function (mappedObjects) {
        this.scope.attr('mappedObjects').replace(
          this._sortObjects(mappedObjects)
        );
      }.bind(this));

      // We are tracking binding changes, so mapped items update accordingly
      binding.list.on('change', function () {
        this.scope.attr('mappedObjects').replace(
          this._sortObjects(binding.list)
        );
      }.bind(this));
    },
    /**
      * Sort objects list by this.scope.sortField, if defined
      * in order defined in this.scope.sortOrder (asc or desc)
      *
      * @param {Array} mappedObjects - the list of objects to be sorted
      *
      * @return {Array} - if this.scope.sortField is defined, mappedObjects
      *                   sorted by field this field;
      *                   if this.scope.sortField is undefined, unsorted
      *                   mappedObjects.
      */
    _sortObjects: function (mappedObjects) {
      let sortField = this.scope.attr('sortField');
      let sortOrder = this.scope.attr('sortOrder');
      if (sortField) {
        return _.sortByOrder(mappedObjects, sortField, sortOrder);
      }
      return mappedObjects;
    },
    events: {
      '[data-toggle=unmap] click': function (el, ev) {
        let instance = el.find('.result').data('result');
        let mappings = this.scope.parentInstance.get_mapping(
          this.scope.mapping);
        let binding;

        ev.stopPropagation();
        // Refactor and show spinner instead (for all lists)
        el.hide();
        binding = _.find(mappings, function (mapping) {
          return mapping.instance.id === instance.id &&
            mapping.instance.type === instance.type;
        });
        _.each(binding.get_mappings(), function (mapping) {
          mapping.refresh()
            .then(function () {
              return mapping.destroy();
            })
            .then(function () {
              if (mapping.documentable) {
                return mapping.documentable.reify();
              }
            })
            .fail(notifierXHR('error'));
        });
      },
    },
  });
})(window.can, window.can.$);
