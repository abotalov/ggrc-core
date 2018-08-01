/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/
(function (root, $, GGRC) {
  'use strict';

  function Popover(element) {
    this.el = element;
    this.$el = $(element);
    this.$body = $('body');
    this.file = this.$el.data('get-template');
    this.template = $(this.get_template());
    this._isShown = false;

    if (!this.template || !this.template.length) {
      return;
    }
    this.init();
    this.bindEvents();
  }
  Popover.prototype.get_template = function () {
    return $.parseHTML(GGRC.Templates[this.file]);
  };
  Popover.prototype.bindEvents = function () {
    this.$el.on('click', $.proxy(this.displayToggle, this));
    this.$body.on('click', $.proxy(this.clickOutside, this));
  };
  Popover.prototype.close = function (evnt) {
    if (evnt) {
      evnt.preventDefault();
    }
    this.popover.hide();
    this._isShown = false;
  };
  Popover.prototype.inElement = function (target, elements) {
    return $.map(elements, function (element) {
      return target.closest(element).length || target.is(element);
    }).some(function (val) {
      return val;
    });
  };
  Popover.prototype.clickOutside = function (evnt) {
    let $target = $(evnt.target);

    if (!this.inElement($target, [this.popover.tip(), this.$el])) {
      this.close();
    }
  };
  Popover.prototype.displayToggle = function (evnt) {
    evnt.preventDefault();

    this.popover[this._isShown ? 'hide' : 'show']();

    if (!this._isShown) {
      this.popover.tip().on('click', '.btn-green', $.proxy(this.close, this));
    }
    this._isShown = !this._isShown;
  };
  Popover.prototype.init = function () {
    this.popover = this.$el.popover({
      trigger: 'manual',
      html: true,
      placement: function (el, src) {
        $(el).addClass('popover-help-wrap');
        return 'bottom';
      }.bind(this),
      title: function () {
        return this.template.find('.popup__title').text();
      }.bind(this),
      content: function () {
        return this.template.find('.popup__content').html();
      }.bind(this),
    }).data('popover');
  };

  function Plugin(option) {
    return this.each(function () {
      let $this = $(this);
      let data = $this.data('popover-template');

      if (!data) {
        $this.data('popover-template', new Popover(this));
      }
    });
  }
  $.fn.popover_template = Plugin;
  $.fn.popover_template.Constructor = Popover;

  $('body').on('mouseover.popover-template', '.popover-template', function (evnt) {
    $(evnt.currentTarget).popover_template();
  });
})(window, jQuery, GGRC);
