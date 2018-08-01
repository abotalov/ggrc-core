/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import BaseTreeItemVM from './tree-item-base-vm';
import './tree-item-extra-info';
import template from './templates/sub-tree-item.mustache';

let viewModel = BaseTreeItemVM.extend({
  define: {
    dueDate: {
      type: 'date',
      get: function () {
        return this.attr('instance.next_due_date') ||
          this.attr('instance.end_date');
      },
    },
    dueDateCssClass: {
      type: 'string',
      get: function () {
        let isOverdue = this.attr('instance.isOverdue');
        return isOverdue ? 'state-overdue' : '';
      },
    },
    isCycleTaskGroupObjectTask: {
      type: 'boolean',
      get: function () {
        return this.attr('instance') instanceof
          CMS.Models.CycleTaskGroupObjectTask;
      },
    },
    cssClasses: {
      type: String,
      get: function () {
        let classes = [];
        let instance = this.attr('instance');

        if (instance.snapshot) {
          classes.push('snapshot');
        }

        if (this.attr('extraCss')) {
          classes = classes.concat(this.attr('extraCss').split(' '));
        }

        return classes.join(' ');
      },
    },
    title: {
      type: String,
      get() {
        const instance = this.attr('instance');
        return (
          instance.attr('title') ||
          instance.attr('description_inline') ||
          instance.attr('name') ||
          instance.attr('email') || ''
        );
      },
    },
  },
  itemSelector: '.sub-item-content',
  extraCss: '@',
});

export default can.Component.extend({
  tag: 'sub-tree-item',
  template,
  viewModel,
  events: {
    inserted: function () {
      this.viewModel.attr('$el', this.element);
    },
    '{viewModel.instance} destroyed'() {
      const element = $(this.element)
        .closest('tree-widget-container');
      can.trigger(element, 'refreshTree');
    },
  },
});
