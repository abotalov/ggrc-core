/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

(function (root, GGRC, $, can) {
  let doc = root.document,
    body = doc.body,
    $win = $(root),
    $doc = $(doc),
    $body = $(body);

  $.migrateMute = true; // turn off console warnings for jQuery-migrate

  function ModelError(message, data) {
    this.name = 'ModelError';
    this.message = message || 'Invalid Model encountered';
    this.data = data;
  }
  ModelError.prototype = Error.prototype;
  root.cms_singularize = function (type) {
    let _type = type.trim().toLowerCase();
    switch (_type) {
      case 'facilities':
        type = type[0] + 'acility';
        break;
      case 'people':
        type = type[0] + 'erson';
        break;
      case 'processes':
        type = type[0] + 'rocess';
        break;
      case 'policies':
        type = type[0] + 'olicy';
        break;
      case 'systems_processes':
        type = type[0] + 'ystem_' + type[8] + 'rocess';
        break;
      default:
        type = type.replace(/s$/, '');
    }
    return type;
  };
  root.calculate_spinner_z_index = function () {
    let zindex = 0;
    $(this).parents().each(function () {
      let z = parseInt($(this).css('z-index'), 10);
      if (z) {
        zindex = z;
        return false;
      }
    });
    return zindex + 10;
  };

  $doc.ready(function () {
    // monitor target, where flash messages are added
    let AUTOHIDE_TIMEOUT = 10000;
    let timeoutId;
    let target = $('section.content div.flash')[0];
    let observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        // check for new nodes
        if (mutation.addedNodes && mutation.addedNodes.length > 0) {
          // remove the success message from non-expandable
          // flash success messages after timeout
          clearTimeout(timeoutId);

          timeoutId = setTimeout(function () {
            $('.flash .alert-autohide').remove();
          }, AUTOHIDE_TIMEOUT);
        }
      });
    });

    let config = {
      attributes: true,
      childList: true,
      characterData: true,
    };

    if (target) {
      observer.observe(target, config);
    }
  });

  $win.load(function () {
    $body.on('click', 'ul.tree-structure .item-main .grcobject,' +
      ' ul.tree-structure .item-main .openclose', function (ev) {
      ev.stopPropagation();
      $(this).openclose();
    });
    // Google Circle CTA Button
    $body.on('mouseenter', '.square-trigger', function () {
      let $this = $(this),
        $popover = $this.closest('.circle-holder').find('.square-popover');

      $popover.slideDown('fast');
      $this.addClass('active');
      return false;
    });
    $body.on('mouseleave', '.square-popover', function () {
      let $this = $(this),
        $trigger = $this.closest('.circle-holder').find('.square-trigger');

      $this.slideUp('fast');
      $trigger.removeClass('active');
      $this.removeClass('active');
      return false;
    });
    // References popup preview
    $body.on('mouseenter', '.new-tree .tree-info a.reference', function () {
      if ($(this).width() > $('.new-tree .tree-info').width()) {
        $(this).addClass('shrink-it');
      }
    });

    // Tab indexing form fields in modal
    $body.on('focus', '.modal', function () {
      $('.wysiwyg-area').each(function () {
        let $this = $(this),
          $textarea = $this.find('textarea.wysihtml5').attr('tabindex'),
          $descriptionField = $this.find('iframe.wysihtml5-sandbox');

        function addingTabindex() {
          $descriptionField.attr('tabindex', $textarea);
        }
        setTimeout(addingTabindex, 100);
      });
    });

    // Prevent link popup in code mode
    $body.on('click', 'a[data-wysihtml5-command=popupCreateLink]', function (e) {
      let $this = $(this);
      if ($this.hasClass('disabled')) {
        // The button is disabled, close the modal immediately
        $('body').find('.bootstrap-wysihtml5-insert-link-modal').modal('hide');
        $this.closest('.wysiwyg-area').find('textarea').focus();
      }
    });
    // top nav dropdown position
    function dropdownPosition() {
      let $this = $(this),
        $dropdown = $this.closest('.hidden-widgets-list').find('.dropdown-menu'),
        $menu_item = $dropdown.find('.inner-nav-item').find('a'),
        offset = $this.offset(),
        win = $(window),
        win_width = win.width();

      if (win_width - offset.left < 322) {
        $dropdown.addClass('right-pos');
      } else {
        $dropdown.removeClass('right-pos');
      }
      if ($menu_item.length === 1) {
        $dropdown.addClass('one-item');
      } else {
        $dropdown.removeClass('one-item');
      }
    }
    $('.dropdown-toggle').on('click', dropdownPosition);
  });
  root.getPageToken = function getPageToken() {
    return $(document.body).data('page-subtype') ||
      $(document.body).data('page-type') ||
      window.location.pathname
        .substring(1, (window.location.pathname + '/').indexOf('/', 1));
  };
  // Make sure GGRC.config is defined (needed to run Karma tests)
  GGRC.config = GGRC.config || {};
})(window, GGRC, jQuery, can);
