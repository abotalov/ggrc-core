# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import nerodia

from lib import base
from lib.page.widget import page_mixins


class WithPageTab(base.WithBrowser):
  def page_tab(self, tab_name):
    return PageTab(self._driver, tab_name)


class PageTab(page_mixins.WithPageElements):
  """Page tab.
  Any method invoked on this class returns `PageTabElementWrapper`.
  `PageTabElementWrapper` is a wrapper around Nerodia elements.
  """

  def __init__(self, driver, tab_name):
    super(page_mixins.WithPageElements, self).__init__(driver)
    self._browser = self._browser
    self._tab_name = tab_name
    self._scope = PageTabElementWrapper(self._browser, self)
    self._tabs_el = self._browser.element(class_name="nav-tabs")

  def __getattr__(self, attr_name):
    """Delegate all methods to container"""
    return getattr(self._scope, attr_name)

  def ensure_tab(self):
    """Ensure that tab is opened"""
    if self._current_tab_name() != self._tab_name:
      self._tabs_el.li(text=self._tab_name).click()

  def _current_tab_name(self):
    """Name of currently opened tab"""
    return self._tabs_el.li(class_name="active").text


class PageTabElementWrapper(object):
  """A wrapper around Nerodia elements.
  When a container attribute is invoked, a method of Nerodia is invoked, and
  a wrapper around returned container is returned.
  When a non-container attribute is invoked, a tab is opened, and result of
  Nerodia's method is returned.
  """

  def __init__(self, el, page_tab):
    self._el = el
    self._page_tab = page_tab

  def __iter__(self):
    self._page_tab.ensure_tab()
    return iter(self._el)

  def __getitem__(self, index):
    self._page_tab.ensure_tab()
    return self._el[index]

  def __getattr__(self, attr_name):
    """Methods from Container and Adjacent classes return new containers,
    without invoking any actions. So they are wrapped.
    Other methods invoke Selenium methods so they are only delegated.
    """
    if self._is_container_method(attr_name):
      def container_function(*args, **kwargs):
        attr = getattr(self._el, attr_name)
        new_container = attr(*args, **kwargs)
        return PageTabElementWrapper(new_container, self._page_tab)
      return container_function
    else:
      self._page_tab.ensure_tab()
      return getattr(self._el, attr_name)

  @staticmethod
  def _is_container_method(attr_name):
    builder_classes = [nerodia.container.Container(),
                       nerodia.adjacent.Adjacent()]
    return any(hasattr(cls, attr_name) for cls in builder_classes)
